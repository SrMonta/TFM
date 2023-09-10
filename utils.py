import prompts
from fastapi import UploadFile, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from pypdf import PdfReader
from helpers import OpenAIHelper
from config import N_PAGES_JOIN
from starlette.background import BackgroundTask
import json
import os

# logger = logging.getLogger('utils')

class Utils:

    SUPPORTED_FILE_TYPES = {'application/pdf'}
    SUPPORTED_QUESTION_TYPES = {1, 2, 3}
    SUPPORTED_RESPONSE_TYPES = {1, 2}
    QUESTION_OPTIONS = ['a', 'b', 'c', 'd']

    @classmethod
    def check_request(cls, file: UploadFile, question_type: int, include_answers: bool, response_type: int, keep_file: bool):
        # Check file type
        cls.check_file_type(cls, file)
        # Check arguments
        cls.check_arguments(cls, question_type, include_answers, response_type, keep_file)

    def check_arguments(cls, question_type: int, include_answers: bool, response_type: int, keep_file: bool):
        # Check question type
        if question_type not in cls.SUPPORTED_QUESTION_TYPES:
            raise HTTPException(status_code=400, detail=f'Question type ({question_type}) not supported. Question types supported: {cls.SUPPORTED_QUESTION_TYPES}')
        # Check include answers
        if not (type(include_answers) is bool):
            raise HTTPException(status_code=400, detail=f'Include answers ({include_answers}) needs to be a boolean (True/False).')
        # Check response type
        if response_type not in cls.SUPPORTED_RESPONSE_TYPES:
            raise HTTPException(status_code=400, detail=f'Response type ({response_type}) not supported. Response types supported: {cls.SUPPORTED_RESPONSE_TYPES}')
        # Check keep file
        if not (type(keep_file) is bool):
            raise HTTPException(status_code=400, detail=f'Keep file ({include_answers}) needs to be a boolean (True/False).')

    def check_file_type(cls, file: UploadFile):
        if file.content_type not in cls.SUPPORTED_FILE_TYPES:
            raise HTTPException(status_code=400, detail=f'File type not supported {file.content_type}. File types supported: {cls.SUPPORTED_FILE_TYPES}')

    @classmethod
    def get_file_content(cls, file: UploadFile) -> list[str]:
        reader = PdfReader(file.file)
        print(f'Reading content for file {file.filename}')
        doc_content = []
        content = ''
        count = 0
        # We skip the first 2 pages (cover + index) and the last one (back cover)
        for p in range(2, len(reader.pages) - 1):
            page = reader.pages[p]
            content += page.extract_text()
            count += 1
            # We split the content of the document every 4 pages
            if count == N_PAGES_JOIN:
                doc_content.append(content.strip())
                content = ''
                count = 0
        # Return the document content (array with strings)
        return doc_content

    def _get_question_prompt(question_type: int) -> str:
        if question_type == 1: #  (1) true/false
            return prompts.prompts['question']['true/false']
        elif question_type == 2: #  (2) single
            return prompts.prompts['question']['single']
        else: # (3)  multiple
            return prompts.prompts['question']['multiple']
        
    def _get_answers_prompt():
        return prompts.prompts['answers']['true']
    
    def _get_format_prompt():
        return prompts.prompts['format']['json']
        
    def _generate_messages(cls, content: str, question_type: int):
        messages = [
            {'role': 'system', 'content': 'Tu objetivo es generar preguntas de tipo test.'}
        ]
        # Question message
        question_message = cls._get_question_prompt(question_type) + f' Texto: """{content}"""'
        messages.append({'role': 'user', 'content': question_message})
        # Include answers
        answers_message = cls._get_answers_prompt()
        messages.append({'role': 'user', 'content': answers_message})
        # Format
        # format_message = cls._get_format_prompt()
        # messages.append({'role': 'user', 'content': format_message})
        return messages
    
    @classmethod
    def get_questions(cls, doc_content: list[str], question_type: int) -> list:
        questions = []
        for c in doc_content:
            request_messages = cls._generate_messages(cls, c, question_type)
            json_questions = OpenAIHelper.generate_questions(request_messages)
            questions.append(json_questions)
        return questions
    
    def _get_json_response(filename: str, questions: list):
        return {
            'filename': filename,
            'questions': questions
        }
    
    def update_file_paths(filename: str, file_path: str):
        with open("./file_paths.json", "r+") as jsonFile:
            data = json.load(jsonFile)
            data[filename.split('.')[0]] = file_path
            jsonFile.seek(0)  # rewind
            json.dump(data, jsonFile)
            jsonFile.truncate()

    def clean_files():
        try:
            # Clean files
            dir_path = './question_files/'
            files = os.listdir(dir_path)
            for file in files:
                file_path = os.path.join(dir_path, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            # Clean files path file
            with open('./file_paths.json', 'w') as jsonFile:
                jsonFile.write('{}')
                jsonFile.close()
            return True
        except Exception as e:
            return False

    def delete_file(path: str):
        os.remove(path=path)

    def get_generated_file(filename: str):
        with open("./file_paths.json", "r+") as jsonFile:
            content = json.load(jsonFile)
            file_path = content.get(filename, None)
            if not file_path:
                jsonFile.close()
                return JSONResponse(status_code=404, content={'message': f'File {filename} does not exist'})
            else:
                jsonFile.close()
                return FileResponse(path=file_path, media_type='text/plain', filename=filename)
    
    def _get_txt_response(cls, filename: str, questions: list, include_answers: bool, keep_file: bool):
        name = filename.split('.')[0]+'_questions.txt'
        path = f'./question_files/{name}'
        f = open(path, 'w', encoding='utf-8')
        for q in questions:
            f.write(f'Pregunta: {q["pregunta"]}\n\n')
            for i, o in enumerate(q['opciones']):
                f.write(f'{cls.QUESTION_OPTIONS[i]}) {o}\n')
            if include_answers:
                f.write(f'\nRespuesta: {q["respuesta_correcta"]}\n\n')
            else:
                f.write('\n')
        if keep_file:
            cls.update_file_paths(filename, path)
            return FileResponse(path=path, media_type='text/plain', filename=name)
        else:
            return FileResponse(path=path, media_type='text/plain', filename=name, background=BackgroundTask(cls.delete_file, path))
        
    def _get_json_questions(cls, questions: list, include_answers: bool):
        res = []
        for question_list in questions:
            if type(question_list) is dict:
                l = question_list['preguntas']
            elif type(question_list) is list:
                l = question_list
            else:
                raise HTTPException(status_code=500, detail='There has been an error while forming the response. Please try again.')
            for e in l:
                obj = {'pregunta': e['pregunta'], 'opciones': e['opciones']}
                if include_answers:
                    obj['respuesta_correcta'] = e['respuesta_correcta']
                res.append(obj)
        return res
    
    @classmethod
    def get_response(cls, filename: str, questions: list, response_type: int, include_answers: bool, keep_file: bool):
        json_questions = cls._get_json_questions(cls, questions, include_answers)
        if response_type == 1: #  txt file
            return cls._get_txt_response(cls, filename, json_questions, include_answers, keep_file)
        elif response_type == 2: #  json
            return cls._get_json_response(filename, json_questions)

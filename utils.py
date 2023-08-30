import prompts
from fastapi import UploadFile, HTTPException
from pypdf import PdfReader
import logging

logger = logging.getLogger('utils')

class Utils:

    SUPPORTED_FILE_TYPES = {'application/pdf'}

    @classmethod
    def check_file_type(cls, file: UploadFile):
        if file.content_type not in cls.SUPPORTED_FILE_TYPES:
            raise HTTPException(status_code=400, detail=f'File type not supported {file.content_type}. File types supported: {cls.SUPPORTED_FILE_TYPES}')

    @classmethod
    def generate_response(cls, questions: str, response_type: int):
        # Generar una respuesta
        # Si es json devolver json con fastapi.responses.JSONResponse o directament con un dict
        # Si es fichero generar un ficher txt con fastapi.responses.FileResponse
        pass

    @classmethod
    def generate_questions(cls, prompt: str, file_content: list[str]) -> str:
        generated_questions = ''
        for c in file_content:
            # Generate prompt to call openai with each chunk of content
            new_prompt = cls.add_content_to_prompt(c, prompt)
            # Call to openai
            # new_questions = cls.generate_questions_openai(...)
            # Append questions to text
            # generated_questions += new_questions
        return generated_questions

    def add_content_to_prompt(file_content: str, prompt: str) -> str:
        new_prompt = prompt + f' Texto: """\n{file_content}\n"""'
        return new_prompt

    @classmethod
    def get_file_content(cls, file: UploadFile) -> list[str]:
        reader = PdfReader(file.file)
        logger.info(f'Reading content for file {file.filename}')
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
            if count == 4:
                doc_content.append(content.strip())
                content = ''
                count = 0
        # Return the document content (array with strings)
        return doc_content

    @classmethod
    def get_prompt(cls, question_type: int, include_answers: bool) -> str:
        prompt = ''
        # Question type
        prompt += cls._question_prompt(question_type)
        # Include answers
        prompt += cls._include_answers(include_answers)

        return prompt
        
    def _question_prompt(question_type: int) -> str:
        '''
        Get the correct question prompt based on the query parameter

        Args:
            question_type: int
                1: true/false questions
                2: single option questions
                3: multiple option questions
        '''
        if question_type == 1: # true/false
            return prompts.prompts['question']['true/false']
        elif question_type == 2: # single
            return prompts.prompts['question']['single']
        elif question_type == 3: # multiple
            return prompts.prompts['question']['multiple']
        else:
            raise Exception(f'Invalud question_type value {question_type}')

    def _include_answers(include_answers: bool) -> str:
        '''
        Include a phrase to make the model include the correct answers for each question

        Args:
            include_answers: bool
        '''
        if include_answers:
            return prompts.prompts['answers']['true']
        else:
            return prompts.prompts['answers']['false']

from fastapi import FastAPI, UploadFile, HTTPException
from pypdf import PdfReader
import datetime
from utils import Utils

app = FastAPI()

# To start server: uvicorn main:app --reload

@app.get('/health')
def health_check():
    return {
        'status': 'healthy',
        'time': datetime.datetime.now()
    }

# Params:
# question_mode (int): mode of the questions (t/f, single, multiple)
# include_answers (bool): to include or not the correct answer
# response_mode (int): how to return (json/txt) (pdf optional to develop)
#
# question_mode
# 1 -> true/false questions
# 2 -> single option
# 3 -> multiple option (peor resultado)
# 4 -> mixto (combinar todo) (no sale, se tiene que combinar llamadas)
def check_question_mode(question_type: int):
    if question_type == 1:
        question_t = 'true/false'
    elif question_type == 2:
        question_t = 'single'
    elif question_type == 3:
        question_t = 'multiple'
    else:
        raise HTTPException(status_code=400, detail=f'Value for question_mode {question_type} not supported')
    return question_t

# include_answers
# true -> include the correct answer
# false -> dont include correct answer
def check_include_answers(include_answers: bool):
    if not isinstance(include_answers, bool):
        return HTTPException(status_code=400, detail=f'Value for include_answers {include_answers} not supported')

# response_mode
# 1 -> json response with the answers
# 2 -> return a txt file with the responses
def check_response_mode(response_type: int):
    if response_type == 1:
        response_t = 'json'
    elif response_type == 2:
        response_t = 'txt'
    else:
        raise HTTPException(status_code=400, detail=f'Value for response {response_type} not supported')
    return response_t

@app.post('/file_info')
def file_info_check(file: UploadFile):
    reader = PdfReader(file.file)
    return {
        'filename': file.filename,
        'number_of_pages': len(reader.pages),
        'filesize': file.size,
        'file_type': file.content_type
    }

# TODO: comprobar valores de los query parameters así como del tipo de fichero que nos llega
# TODO: actualizar prompts para tener el numero de preguntas correctas
# TODO: SI AL FINAL DAMOS OPCION DE MEZCLAR TIPOS DE PREGUNTAS HAY QUE VER COMO HACERLO
# TODO: ACTUALIZAR RUTA DE /PROMPT A /QUESTIONS O SIMILAR

@app.post('/prompt')
def generate_prompt(file: UploadFile, question_type: int = 1, include_answers: bool = True, response_type: int = 1):
    # Check file type
    Utils.check_file_type(file)
    # File read
    file_content = Utils.get_file_content(file)
    # Get base prompt
    prompt = Utils.get_prompt(question_type, include_answers)
    # Call to openai TODO:
    questions = Utils.generate_questions(prompt, file_content)
    # Generate response and return
    return Utils.generate_response(questions, response_type)

    # # Return
    # return {
    #     'file_name': file.filename,
    #     'prompt': prompt,
    #     'question_type': question_type,
    #     'include_answers': include_answers,
    #     'response_type': response_type
    # }


from fastapi import FastAPI, UploadFile, HTTPException
from pypdf import PdfReader
import datetime

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
# 3 -> multiple option
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

@app.get('/params')
def params_check(question_type: int = 1, include_answers: bool = True, response_type: int = 1):
    q_mode = check_question_mode(question_type)
    i_answers = check_include_answers(include_answers)
    r_mode = check_response_mode(response_type)
    return {
        'question_mode': q_mode,
        'include_answers': i_answers,
        'response_mode': r_mode
    }

@app.post('/file')
def file_check(file: UploadFile):
    reader = PdfReader(file.file)
    n_pages = len(reader.pages)
    page = reader.pages[0]
    text = page.extract_text()
    clean_text = text.rstrip('\n').strip().replace('\\n', '')
    print(clean_text)
    return {
        'n_pages': n_pages,
        'text': clean_text
    }

@app.post('/file_info')
def file_info_check(file: UploadFile):
    reader = PdfReader(file.file)
    return {
        'filename': file.filename,
        'number_of_pages': len(reader.pages),
        'filesize': file.size,
        'file_type': file.content_type
    }

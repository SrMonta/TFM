from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import JSONResponse
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

@app.post('/file_info')
def file_info_check(file: UploadFile):
    reader = PdfReader(file.file)
    return {
        'filename': file.filename,
        'number_of_pages': len(reader.pages),
        'filesize': file.size,
        'file_type': file.content_type
    }

# Params:
# question_mode (int): mode of the questions (t/f, single, multiple)
# include_answers (bool): to include or not the correct answer
# response_mode (int): how to return (json/txt) (pdf optional to develop)

# question_mode
# 1 -> true/false questions
# 2 -> single option
# 3 -> multiple option (peor resultado)

# include_answers
# true -> include the correct answer
# false -> dont include correct answer

# response_mode
# 1 -> return a txt file with the responses
# 2 -> json response with the answers

# keep_file
# true -> no borrar archivo
# false -> borrar archivo
# TODO:

@app.post('/questions')
def generate_questions(file: UploadFile, question_type: int = 1, include_answers: bool = True, response_type: int = 1, keep_file: bool = False):
    # Check request
    Utils.check_request(file, question_type, include_answers, response_type, keep_file)
    # File read
    file_content = Utils.get_file_content(file)
    # Generate questions
    questions = Utils.get_questions(file_content, question_type)
    # Generate response
    return Utils.get_response(file.filename, questions, response_type, include_answers, keep_file)

@app.get('/question_file/{filename}')
def retrieve_generated_file(filename):
    return Utils.get_generated_file(filename)

@app.get('/clean_files')
def clean_files():
    if Utils.clean_files():
        return JSONResponse(status_code=200, content={'message': 'Stored generated files deleted'})
    else:
        return JSONResponse(status_code=400, content={'message': 'There has been an error while deleting the files.'})
    

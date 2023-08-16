from fastapi import FastAPI, File, UploadFile
from pypdf import PdfReader
import datetime

app = FastAPI()

@app.get('/health')
def health_check():
    return {
        'status': 'healthy',
        'time': datetime.datetime.now()
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

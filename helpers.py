import openai
from config import OPEN_AI_KEY, OPEN_AI_COMPLETION_MODEL_1, N_PAGES_JOIN, N_QUESTIONS_JOIN
from fastapi import HTTPException
import json

class OpenAIHelper:

    # OpenAI api key
    openai.api_key = OPEN_AI_KEY

    # @classmethod
    # def create_completion(cls, message: str):
    #     try:
    #         print(f'Making call to openai to generate {N_QUESTIONS_JOIN} questions')
    #         response = openai.ChatCompletion.create(
    #             model=OPEN_AI_COMPLETION_MODEL_1,
    #             messages=[{
    #                 'role': 'user',
    #                 'content': message
    #             }]
    #         )
    #         return response.choices[0].message.content
    #     except Exception as e:
    #         raise HTTPException(status_code=413, detail=f'There has been an error on the request to openai. Error: {e}')


    @classmethod
    def generate_questions(cls, messages: list):
        try:
            retries = 3
            count = 0
            while count < retries:
                print(f'Making call to openai to generate {N_QUESTIONS_JOIN} questions.')
                response = openai.ChatCompletion.create(
                    model=OPEN_AI_COMPLETION_MODEL_1,
                    messages=messages
                )
                generated = response.choices[0].message.content
                try:
                    json_questions = json.loads(generated)
                    return json_questions
                except:
                    count+=1
                    print(f'Invalid json after openai request. Request {count}/{retries}. Retry {count}.')
            raise HTTPException(status_code=429, detail=f'Failed to get questions after {retries} retries.')
        except Exception as e:
            raise HTTPException(status_code=413, detail=f'There has been an error on the request to openai. Error: {e}')
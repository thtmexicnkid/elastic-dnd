# Elastic D&D
# Author: thtmexicnkid
# Last Updated: 10/04/2023
# 
# FastAPI app that facilitates Virtual DM processes and whatever else I think of.

import uvicorn
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message":"Hello World"}

@app.get("/get_vector_object/{text}")
async def get_vector_object(text):
    import openai
    
    openai.api_key = "API_KEY"
    embedding_model = "text-embedding-ada-002"
    openai_embedding = openai.Embedding.create(input=text, model=embedding_model)

    return openai_embedding["data"][0]["embedding"]

@app.get("/get_question_answer/{question}/{query_results}")
async def get_question_answer(question,query_results):
    import openai
    
    summary = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Answer the following question:" 
            + question 
            + "by using the following text:" 
            + query_results},
        ]
    )

    answers = []
    for choice in summary.choices:
        answers.append(choice.message.content)

    return answers

if __name__ == '__main__':
    uvicorn.run("main:app", port=8000, host='0.0.0.0', reload=True)

from fastapi import FastAPI

app = FastAPI()

@app.get('/')
async def root():
    return {'message': 'BLOG_AI API'}

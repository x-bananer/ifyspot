from fastapi import FastAPI
from app import auth_routes

app = FastAPI()

app.include_router(auth_routes.router)

@app.get('/')
def root():
    return {'status': 'success'}
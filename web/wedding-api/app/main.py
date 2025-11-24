from fastapi import FastAPI
from app.config import settings
from app.api.v1.api import api_router

app = FastAPI(title=settings.PROJECT_NAME, version="1.0.0")

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def read_root():
    return {"message": "Welcome to Wedding SaaS API"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

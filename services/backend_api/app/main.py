"""
Main FastAPI application entrypoint
"""
from fastapi import FastAPI
from .api import router as api_router

app = FastAPI(
    title="Financial RAG API",
    description="API for the Financial News RAG Analyzer",
    version="1.0.0"
)

app.include_router(api_router, prefix="/api/v1", tags=["RAG"])

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the Financial RAG API. Visit /docs for documentation."}
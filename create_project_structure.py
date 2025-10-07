import os

# Define the base directory
base_dir = "financial-rag-analyzer"

# Folder structure
folders = [
    "config",
    "services/backend_api/app",
    "services/data_pipeline/app",
    "frontend",
]

# Files to create (with optional starter content)
files = {
    ".env": "",
    ".gitignore": "__pycache__/\n*.pyc\n.env\nvenv/\n.DS_Store\n",
    "README.md": "# Financial RAG Analyzer\n\nAn AI-powered financial document analysis tool.",
    "docker-compose.yml": """version: '3.8'
services:
  backend_api:
    build: ./services/backend_api
    container_name: backend_api
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      - data_pipeline

  data_pipeline:
    build: ./services/data_pipeline
    container_name: data_pipeline
    env_file:
      - .env

  frontend:
    build: ./frontend
    container_name: frontend
    ports:
      - "8501:8501"
    env_file:
      - .env
    depends_on:
      - backend_api
""",
    "config/config.yaml": """# Configuration file for Financial RAG Analyzer
database:
  uri: "sqlite:///data.db"
vector_store:
  type: "faiss"
  path: "artifacts/vector_store"
scraper:
  sources:
    - "https://finance.yahoo.com"
    - "https://www.investing.com"
""",

    # Backend API
    "services/backend_api/app/__init__.py": "",
    "services/backend_api/app/main.py": """from fastapi import FastAPI
from .api import router

app = FastAPI(title="Financial RAG Backend API")

app.include_router(router)

@app.get("/")
def root():
    return {"message": "Financial RAG Analyzer Backend is running!"}
""",
    "services/backend_api/app/api.py": """from fastapi import APIRouter
from .schemas import QueryRequest
from .core import RAGProcessor

router = APIRouter()
rag = RAGProcessor()

@router.post("/query")
def analyze_query(request: QueryRequest):
    response = rag.process(request.query)
    return {"result": response}
""",
    "services/backend_api/app/core.py": """class RAGProcessor:
    def __init__(self):
        pass

    def process(self, query: str):
        return f"Processed financial insight for query: {query}"
""",
    "services/backend_api/app/schemas.py": """from pydantic import BaseModel

class QueryRequest(BaseModel):
    query: str
""",
    "services/backend_api/Dockerfile": """FROM python:3.10-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
""",
    "services/backend_api/requirements.txt": "fastapi\nuvicorn\npydantic\nrequests\n",

    # Data Pipeline
    "services/data_pipeline/app/__init__.py": "",
    "services/data_pipeline/app/scraper.py": """import requests
from bs4 import BeautifulSoup

def scrape_financial_news(url: str):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    headlines = [h.text for h in soup.find_all('h3')]
    return headlines
""",
    "services/data_pipeline/app/data_processor.py": """import pandas as pd

def clean_data(data):
    df = pd.DataFrame(data, columns=['headline'])
    df.dropna(inplace=True)
    return df
""",
    "services/data_pipeline/app/vector_store.py": """import faiss
import numpy as np

def create_vector_store(vectors):
    dim = vectors.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(vectors)
    return index
""",
    "services/data_pipeline/app/pipeline.py": """from .scraper import scrape_financial_news
from .data_processor import clean_data

def run_pipeline():
    urls = ["https://finance.yahoo.com", "https://www.investing.com"]
    all_news = []
    for url in urls:
        all_news.extend(scrape_financial_news(url))
    clean_df = clean_data(all_news)
    print("Pipeline complete. Processed records:", len(clean_df))
""",
    "services/data_pipeline/requirements.txt": "requests\nbeautifulsoup4\npandas\nfaiss-cpu\n",

    # Frontend
    "frontend/app.py": """import streamlit as st
import requests

st.title("💹 Financial RAG Analyzer")

query = st.text_input("Enter your financial query:")
if st.button("Analyze"):
    response = requests.post("http://localhost:8000/query", json={"query": query})
    st.write(response.json()["result"])
""",
    "frontend/requirements.txt": "streamlit\nrequests\n",
}

# Create folders
for folder in folders:
    os.makedirs(os.path.join(base_dir, folder), exist_ok=True)

# Create files with content
for filepath, content in files.items():
    full_path = os.path.join(base_dir, filepath)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

print(f"✅ Project structure created successfully at: {os.path.abspath(base_dir)}")

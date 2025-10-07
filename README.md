📈 Financial News RAG Analyzer
This project is a sophisticated, end-to-end Retrieval-Augmented Generation (RAG) system designed for real-time financial news analysis. It features a modern, decoupled microservices architecture, making it scalable, maintainable, and production-ready.

The entire system is designed to run locally without requiring any paid API keys, leveraging the power of open-source models through Ollama.

✨ Key Features
Decoupled Microservices: A robust FastAPI backend for the AI logic, a sleek Streamlit frontend for user interaction, and a standalone Data Pipeline for scraping and ingestion.

Automated Data Ingestion: The data pipeline is designed to scrape multiple financial news sources (The Economic Times, Livemint, Business Standard, etc.) in a configurable way.

Local First AI: Powered by a local LLM (e.g., tinyllama, llama3) served via Ollama, ensuring privacy and zero cost.

Containerized & Orchestrated: The entire application stack is containerized with Docker and managed with Docker Compose for easy, one-command setup.

Advanced RAG Pipeline:

Metadata Filtering: Filter news sources directly from the UI before asking a question.

Conversational Memory: The chatbot remembers the context of the conversation for follow-up questions.

Polished User Experience:

Real-time response streaming.

Clear sourcing for every answer.

Sidebar with live database statistics.

🏛️ Architecture
The project follows a modern 3-tier architecture, separating presentation, logic, and data.

Data Pipeline: A Python service that runs on-demand or on a schedule. It scrapes news, processes the text, and populates the ChromaDB vector store.

Backend (FastAPI): A containerized API that handles all AI logic. It receives queries, performs similarity searches on the vector DB, orchestrates the RAG chain with Ollama, and streams responses.

Frontend (Streamlit): A containerized web application that provides the user interface. It communicates with the backend via HTTP requests.

🚀 Getting Started
Prerequisites
Docker & Docker Compose

Python 3.10+

Ollama installed and running on your host machine.

Setup & Run
Clone the repository:

git clone <your-repo-url>
cd financial-rag-analyzer

Prepare the Local LLM:

Pull the model specified in config/config.yaml (e.g., tinyllama).

ollama pull tinyllama

Run the Data Pipeline (First-Time Setup):

This script scrapes the news and builds your vector database.

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # or .\venv\Scripts\activate on Windows

# Install dependencies and run the pipeline
cd services/data_pipeline
pip install -r requirements.txt
python -m app.pipeline

# Return to the root directory
cd ../..
deactivate

Launch the Full Application:

From the root directory, start the backend and frontend services.

docker-compose up --build

The Streamlit frontend will be available at http://localhost:8501.

The FastAPI backend API documentation will be at http://localhost:8000/docs.
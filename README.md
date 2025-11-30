📈 Financial News RAG Analyzer
A Fully Local, Production-Ready Retrieval-Augmented Generation System for Financial Insights  

🧠 Overview
Financial News RAG Analyzer is an advanced, end-to-end Retrieval-Augmented Generation (RAG) platform for real-time financial news analysis.It delivers context-aware, explainable, and interactive intelligence by combining large language models with continuously updated financial data — all running completely locally, with no paid APIs or cloud dependencies.  
Built with a modern, decoupled microservices architecture, the system is scalable, maintainable, and production-ready — ideal for researchers, developers, and financial analysts.  

✨ Key Features
🔹 Decoupled Microservices Architecture

Backend (FastAPI): Manages all AI logic, RAG orchestration, and query handling.  
Frontend (Streamlit): A responsive and intuitive web interface for user queries.  
Data Pipeline: Handles web scraping, text processing, and vector store creation.

🔹 Automated Financial Data Ingestion

Continuously scrapes multiple news outlets — The Economic Times, Livemint, Business Standard, etc.  
Uses a YAML-based configuration system for easy addition or removal of sources.

🔹 100% Local AI Stack

Powered by Ollama and open-source models like tinyllama or llama3.  
Runs completely offline — ensuring data privacy and zero operational cost.

🔹 Advanced RAG Pipeline

Metadata Filtering: Filter news by source or category before querying.  
Conversational Memory: Maintains chat context for follow-up questions.  
Source Transparency: Every response includes cited sources and context.

🔹 Production-Ready Deployment

Containerized Services: Each component runs in its own Docker container.  
One-Command Orchestration: Managed via Docker Compose for simplicity.  
Streaming Responses: Real-time token-level output for smooth UX.


🏛️ System Architecture
The application follows a 3-tier architecture, cleanly separating data, logic, and presentation layers.  
financial-rag-analyzer/
├── config/
│   └── config.yaml        # Global configuration (LLM, sources, etc.)
├── services/
│   ├── data_pipeline/     # Scraper and vector store builder
│   ├── backend_api/       # FastAPI RAG backend
│   └── frontend_ui/       # Streamlit frontend interface
└── docker-compose.yml     # Service orchestration

1. Data Pipeline
A Python service that scrapes financial news, cleans text, and stores embeddings in ChromaDB for fast semantic retrieval.  
2. Backend (FastAPI)
Implements the RAG engine: retrieves contextually relevant documents, queries the local LLM (via Ollama), and streams responses back to the frontend.  
3. Frontend (Streamlit)
Provides an elegant, interactive UI for question answering, source filtering, and monitoring live database statistics.  

🚀 Getting Started
Prerequisites
Before running the project, ensure you have:  

Docker & Docker Compose  
Python 3.10+  
Ollama installed and running locally


1. Clone the Repository
git clone https://github.com/Trishapaul5/financial-rag-analyzer.git
cd financial-rag-analyzer

2. Prepare the Local LLM
Pull the model defined in your configuration file (e.g., tinyllama):
ollama pull tinyllama

3. Run the Data Pipeline (First-Time Setup)
This will scrape financial news sources and populate your local vector database.
cd services/data_pipeline
python -m venv venv
source venv/bin/activate        # (Use .\venv\Scripts\activate on Windows)
pip install -r requirements.txt
python -m app.pipeline
deactivate
cd ../..

4. Launch the Application
Start all microservices using Docker Compose:
docker-compose up --build

Once launched:  

🌐 Frontend (Streamlit): http://localhost:8501  
⚙️ Backend API (FastAPI Docs): http://localhost:8000/docs

🧩 Example Workflow

Run the containers with Docker Compose.  
Open the Streamlit dashboard in your browser.  
Filter your preferred sources (e.g., Economic Times, past 7 days).  
Ask a question like:“What are the latest updates on RBI’s monetary policy stance?”  
View detailed, source-backed insights in real time.


⚙️ Tech Stack



Layer
Technology
Purpose



Frontend
Streamlit
Interactive user interface


Backend
FastAPI
RAG orchestration and inference API


Data Layer
ChromaDB
Vector database for embeddings


LLM Engine
Ollama + TinyLLaMA / LLaMA3
Local inference


Scraping
BeautifulSoup, Requests
Data collection


Containerization
Docker, Docker Compose
Deployment & orchestration



📚 Future Enhancements

🔁 Scheduled scraping with CRON or Airflow integration  
📊 Trend visualization dashboards (sentiment, frequency, impact)  
🔒 User authentication and multi-user session support  
🌍 Expanded coverage with multilingual news analysis


🧑‍💻 Contributing
Contributions are welcome!Please open an issue or submit a pull request if you’d like to add features or improve functionality.  

🪪 License
This project is released under the MIT License.See the LICENSE file for more details.  

💬 Empowering financial analysis with open, local, and intelligent AI.

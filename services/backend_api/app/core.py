
import os
import yaml
import logging
from dotenv import load_dotenv
from typing import Dict, List, Optional

# LangChain components for building the RAG chain
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate

# Community integrations for LLMs and Vector Stores
from langchain_community.llms import Ollama
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import AzureChatOpenAI

# Load environment variables (if any)
load_dotenv()

# Setup professional logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RAGEngine:
    """The enhanced RAG engine with conversational memory and metadata filtering."""

    def __init__(self):
        """Initializes the RAG Engine by loading all necessary components from configuration."""
        logger.info("Initializing RAG Engine...")

        # Use the absolute path for the config file as mapped in docker-compose.yml
        config_path = '/home/app/config/config.yaml'
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        self._load_components()
        # In-memory session store for managing separate conversation histories for each user
        self.conversational_memory: Dict[str, ConversationBufferMemory] = {}
        logger.info("RAG Engine initialized successfully.")

    def get_db_stats(self) -> Dict:
        """
        Returns statistics about the vector database for the frontend sidebar.
        This allows the UI to display the number of indexed documents and available sources.
        """
        try:
            collection = self.vectorstore._collection
            count = collection.count()
            # A robust way to get all unique source names from the database metadata
            metadata = collection.get(include=["metadatas"])
            sources = list(set(meta.get('source', 'Unknown') for meta in metadata.get('metadatas', [])))
            return {"total_documents": count, "sources": sorted(sources)}
        except Exception as e:
            logger.error(f"Could not get DB stats: {e}")
            return {"total_documents": 0, "sources": []}

    def _load_components(self):
        """Loads the embedding model, vector store, and the language model."""
        # 1. Load Embeddings Model (runs on CPU)
        self.embeddings = HuggingFaceEmbeddings(
            model_name=self.config['embeddings']['model'],
            model_kwargs={'device': 'cpu'}
        )

        # 2. Load Vector Store from disk using the correct absolute path
        self.vectorstore = Chroma(
            persist_directory='/home/app/chroma_db',
            embedding_function=self.embeddings,
            collection_name=self.config['vector_db']['collection_name']
        )

        # 3. Initialize the LLM based on the configured provider
        provider = self.config['llm']['provider']
        if provider == 'ollama':
            self.llm = Ollama(
                base_url="http://host.docker.internal:11434", # Special Docker DNS to reach the host
                model=self.config['llm']['model']
            )
            logger.info(f"Using Ollama as LLM provider with model '{self.config['llm']['model']}'.")
        elif provider == 'azure_openai':
            # This block remains for future use if you get an Azure key
            self.llm = AzureChatOpenAI(
                azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
                api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                api_version="2024-02-01",
                deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
                temperature=self.config['llm']['temperature'],
                max_tokens=self.config['llm']['max_tokens'],
                streaming=True
            )
            logger.info("Using Azure OpenAI as LLM provider.")
        else:
            raise ValueError(f"Unsupported LLM provider configured: {provider}")

    def _get_conversational_chain(self, session_id: str, filters: Optional[Dict] = None):
        """
        Creates or retrieves a unique conversational chain for a given user session,
        applying any specified metadata filters.
        """
        if session_id not in self.conversational_memory:
            self.conversational_memory[session_id] = ConversationBufferMemory(
                memory_key="chat_history", return_messages=True, output_key="answer"
            )

        memory = self.conversational_memory[session_id]

        search_kwargs = {"k": self.config['rag']['top_k']}
        if filters:
            search_kwargs['filter'] = filters
            logger.info(f"Applying filter to retriever: {filters}")

        retriever = self.vectorstore.as_retriever(
            search_type=self.config['rag']['retrieval_type'],
            search_kwargs=search_kwargs
        )

        # Define the prompt template that will be sent to the LLM
        prompt_template = """You are a professional financial news analyst AI. Use the following context and chat history to answer the question.
        Provide a detailed, insightful answer based ONLY on the provided context. If the context is insufficient, state that you cannot find relevant information.

        Context:
        {context}

        Chat History:
        {chat_history}

        Question: {question}

        Answer:"""
        PROMPT = PromptTemplate(template=prompt_template, input_variables=["context", "chat_history", "question"])

        # Create the full conversational chain
        return ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=retriever,
            memory=memory,
            return_source_documents=True,
            combine_docs_chain_kwargs={"prompt": PROMPT},
            verbose=False # Set to True for more detailed debugging logs
        )

    async def stream_query(self, query: str, session_id: str, sources: Optional[List[str]] = None):
        """
        Handles an incoming query by creating a filtered chain, streaming the LLM's answer,
        and finally appending the source documents.
        """
        logger.info(f"Streaming query for session '{session_id}' with source filters: {sources}")

        filters = None
        if sources:
            filters = {"source": {"$in": sources}}

        chain = self._get_conversational_chain(session_id, filters)

        source_documents = []
        async for chunk in chain.astream({"question": query}):
            if "answer" in chunk:
                yield chunk["answer"] # Stream the answer part
            if "source_documents" in chunk:
                source_documents.extend(chunk['source_documents'])

        # After the answer is complete, stream the formatted sources
        if source_documents:
            # Deduplicate sources based on URL to avoid repetition
            unique_sources = {doc.metadata['url']: doc for doc in source_documents}.values()
            sources_text = "\n\n---\n**Sources:**\n"
            for i, doc in enumerate(unique_sources, 1):
                title = doc.metadata.get('title', 'Unknown Title')
                url = doc.metadata.get('url', '#')
                sources_text += f"{i}. [{title}]({url})\n"
            yield sources_text


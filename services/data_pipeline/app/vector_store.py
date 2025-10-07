"""
Vector Store Manager using ChromaDB
"""
import logging
from typing import List, Dict
from langchain.schema import Document
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VectorStoreManager:
    """Manages ChromaDB vector store operations."""
    def __init__(self, config: Dict):
        self.db_config = config.get('vector_db', {})
        self.embeddings_config = config.get('embeddings', {})
        self.persist_directory = self.db_config.get('persist_directory')
        self.collection_name = self.db_config.get('collection_name')
        
        logger.info(f"Loading embedding model: {self.embeddings_config.get('model')}")
        self.embeddings = HuggingFaceEmbeddings(
            model_name=self.embeddings_config.get('model'),
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )

    def create_or_update_vectorstore(self, documents: List[Document]):
        """
        Creates a new vector store or updates an existing one.
        Chroma's `from_documents` will create or load and add to the collection.
        """
        logger.info(f"Creating/updating vector store with {len(documents)} documents...")
        
        vectorstore = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            persist_directory=self.persist_directory,
            collection_name=self.collection_name
        )
        
        logger.info(f"Persisting vector store to {self.persist_directory}")
        vectorstore.persist()
        logger.info("Vector store updated and persisted successfully.")
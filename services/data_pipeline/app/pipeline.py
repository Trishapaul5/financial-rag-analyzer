"""
Data Processor with various chunking strategies
"""
import re
import logging
from typing import List, Dict
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataProcessor:
    """Processes raw articles into clean, chunked documents for vectorization."""
    def __init__(self, config: Dict):
        self.config = config.get('chunking', {})

    def _clean_text(self, text: str) -> str:
        """Performs basic text cleaning."""
        text = re.sub(r'\s+', ' ', text) # Collapse whitespace
        text = re.sub(r'(\r\n|\n|\r)', ' ', text) # Remove newlines
        return text.strip()

    def process_articles(self, articles: List[Dict]) -> List[Document]:
        """
        Takes a list of article dictionaries and converts them into LangChain Documents
        with metadata, ready for ingestion.
        """
        all_documents = []
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.config.get('chunk_size', 800),
            chunk_overlap=self.config.get('chunk_overlap', 100),
            length_function=len
        )
        
        for article in articles:
            if not article.get('text'):
                continue

            cleaned_text = self._clean_text(article['text'])
            
            # **THE FIX**: Explicitly handle None values to ensure all metadata
            # values are strings, which ChromaDB requires.
            publish_date = article.get('publish_date')
            
            metadata = {
                'title': str(article.get('title', 'N/A')),
                'source': str(article.get('source', 'N/A')),
                'url': str(article.get('url', 'N/A')),
                'publish_date': str(publish_date) if publish_date else 'N/A',
                'section': str(article.get('section', 'N/A'))
            }
            
            chunks = splitter.split_text(cleaned_text)
            
            for i, chunk_text in enumerate(chunks):
                doc = Document(
                    page_content=chunk_text,
                    metadata={**metadata, 'chunk_index': i}
                )
                all_documents.append(doc)

        logger.info(f"Processed {len(articles)} articles into {len(all_documents)} document chunks.")
        return all_documents
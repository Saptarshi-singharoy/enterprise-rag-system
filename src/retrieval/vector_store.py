from typing import List, Optional, Dict, Any
from abc import ABC, abstractmethod

from langchain_classic.schema import Document
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

from ..core.config import get_settings
from ..core.logging import get_logger
from..core.exceptions import RetrievalError

logger= get_logger(__name__)
settings = get_settings()

class VectorStore(ABC):
    """Abstract base class for vector stores"""

    @abstractmethod
    async def add_documents(self, documents: List[Document]) -> List[str]:
        """Add documents to vector store"""
        pass

    @abstractmethod
    async def similarity_search(
        self,
        query: str,
        k: int = 5,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[Document]:
        """Search for similar documents"""
        pass

    @abstractmethod
    async def delete_documents(
        self,
        ids: List[str]
    ) -> None:
        """Delete documents by IDs"""
        pass

class ChromaVectorStore(VectorStore):
    """Chroma DB implementation"""

    def __init__(self):
        super().__init__()
        self.embeddings = OpenAIEmbeddings(
            model=settings.OPENAI_EMBEDDING_MODEL,
            openai_api_key=settings.OPENAI_API_KEY
        )

        self.store = Chroma(
            persist_directory=settings.CHROMA_PERSIST_DIR,
            embedding_function=self.embeddings
        )

        logger.info("Chroma Vector Store initialized")
    
    async def add_documents(self, documents: List[Document]) -> List[str]:
        """Add documents to ChromaDB"""
        try:
            ids = self.store.aadd_documents(documents)
            logger.info(f"Added {len(documents)} documents to vector store")
            return ids
        except Exception as e:
            logger.error(f"Failed to add documents: {str(e)}")
            raise RetrievalError(f"Add documents failed: {str(e)}") from e

    async def similarity_search(
        self,
        query: str,
        k: int = 5,
        filter: Optional[Dict[str, Any]] = None
    )-> List[Document]:
        """Search for similar documents"""
        try:
            results = self.store.similarity_search(
                query, k=k, filter=filter
            )
            logger.info(f"Retrieved {len(results)} documents for query")
            return results
        except RetrievalError as e:
            logger.error(f"Similarity search failed: {str(e)}")
            raise RetrievalError(
                f"Similarity search failed: {str(e)}"
            ) from e
        
    async def delete_documents(self, ids: List[str]) -> None:
        """Delete documents by IDs"""
        try:
            self.store.delete(ids)
            logger.info(f"Deleted {len(ids)} documents")
        except Exception as e:
            logger.error(f"Delete failed: {str(e)}")
            raise RetrievalError(f"Delete failed: {str(e)}") from e
        

def get_vector_store() -> VectorStore:
    """Factory function to get vector store instance"""
    if settings.VECTOR_DB_TYPE == 'chromadb':
        return ChromaVectorStore()
    else:
        raise ValueError(f"Unsupported vector DB: {settings.VECTOR_DB_TYPE}")

        

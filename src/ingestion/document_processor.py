from typing import List, Dict, Any, Optional
from pathlib import Path
import hashlib
from datetime import datetime

from langchain_classic.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    PyPDFLoader,
    UnstructuredWordDocumentLoader,
    UnstructuredMarkdownLoader,
    TextLoader
)
from langchain_classic.schema import Document

from ..core.config import get_settings
from ..core.logging import get_logger
from ..core.exceptions import DocumentProcessingError

logger = get_logger(__name__)
settings = get_settings()

class DocumentProcessor:
    """Handles Document loading, chunking and preprocessing"""

    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunnk_overlap=settings.CHUNK_OVERLAP,
            length_function=len,
            separators=["\n\n","\n", ". ", " ", ""]
        )

        self.loaders = {
            ".pdf": PyPDFLoader,
            ".docx": UnstructuredWordDocumentLoader,
            ".txt":TextLoader,
            ".md": UnstructuredMarkdownLoader
        }
    
    def process_document(self, file_path: Path, metadata: Optional[Dict[str, Any]]=None) -> List[Document]:
        """
        Process a single document: load, chunk, and enrich with metadata
        
        Args:
            file_path: Path to the document
            metadata: Additional metadata to attach
            
        Returns:
            List of Document chunks with metadata
        """
        try:
            logger.info(f"Processing document: {file_path}")

            # Validate File
            self._validate_file(file_path)

            # Load document
            documents = self._load_document(file_path)

            # Chunk documents
            chunks = self.text_splitter.split_documents(documents)

            # Enrich with metadata
            enriched_chunks = self._enrich_metadata(chunks, file_path, metadata or {})

            logger.info(
                f"Processed {file_path}: {len(chunks)} chunks created."
            )

            return enriched_chunks


        except Exception as e:
            logger.error(f"Failed to process {file_path}: {str(e)}")
            raise DocumentProcessingError(
                f"Document processing failed: {str(e)}"
            ) from e
    
    def _validate_file(self, file_path: Path) -> None:
        """Validate file exists and is supported format"""
        if not file_path.exists():
            raise DocumentProcessingError(
                f"File not Found: {file_path}"
            )
        if file_path.suffix not in settings.SUPPORTED_FORMATS:
            raise DocumentProcessingError(
                f"Unsupported format: {file_path.suffix}"
            )
        file_size_mb = file_path.stat().st_size / (1024*1024)
        if file_size_mb > settings.MAX_DOCUMENT_SIZE_MB:
            raise DocumentProcessingError(
                f"File too large: {file_size_mb:.2f}MB"
                f"Max Size: {settings.MAX_DOCUMENT_SIZE_MB}MB"
            )
        
    def _load_document(self, file_path: Path) -> List[Document]:
        """Load document with appropriate loader"""
        loader_class = self.loaders.get(file_path.suffix)

        if not loader_class:
            raise DocumentProcessingError(
                f"No loader for {file_path.suffix}"
            )
        
        loader = loader_class(str(file_path))
        return loader.load()
    
    def _enrich_metadata(self, chunks:List[Document], file_path: Path, custom_metadata: Dict[str, Any]) -> List[Document]:
        """Add metadata to each chunk"""

        file_hash = self._calculate_file_hash(file_path)

        for i, chunk in enumerate(chunks):
            chunk.metadata.update({
                "source": str(file_path),
                "file_name": file_path.name,
                "file_type": file_path.suffix,
                "file_hash": file_hash,
                "chunk_index": i,
                "total_chunks": len(chunks),
                "processed_at": datetime.now().isoformat(),
                "chunk_size": len(chunk.page_content),
                **custom_metadata,
            })
        return chunks


    @staticmethod
    def _calculate_file_hash(file_path: Path) -> str:
        """calculate sha256 hash of file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()


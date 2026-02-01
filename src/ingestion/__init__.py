"""
Document ingestion and processing pipeline
"""

from .document_processor import DocumentProcessor
from .metadata_enricher import MetadataEnricher

# Note: embeddings module would be here if we create a separate embeddings.py
# from .embeddings import EmbeddingGenerator

__all__ = [
    "DocumentProcessor",
    "MetadataEnricher",
    # "EmbeddingGenerator",  # Uncomment when implemented
]
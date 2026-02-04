# ============================================================================
# FILE: src/__init__.py
# ============================================================================
"""
Enterprise Knowledge Assistant - RAG System

A production-ready Retrieval Augmented Generation system for querying
enterprise documents with grounded, validated responses.
"""

__version__ = "1.0.0"
__author__ = "Enterprise AI Team"
__license__ = "MIT"

from .config import get_settings, Settings
from .logging import setup_logging, get_logger

# Initialize logging on package import
settings = get_settings()
setup_logging(settings.LOG_LEVEL)

__all__ = [
    "get_settings",
    "setup_logging",
    "get_logger",
]


# ============================================================================
# FILE: src/core/__init__.py
# ============================================================================
"""
Core functionality and configuration
"""

from .config import get_settings, Settings
from .logging import setup_logging, get_logger
from .exceptions import (
    RAGSystemException,
    DocumentProcessingError,
    EmbeddingGenerationError,
    RetrievalError,
    GenerationError,
    ValidationError,
    RateLimitExceeded,
    CacheError,
)

__all__ = [
    # Configuration
    "get_settings",
    "Settings",
    
    # Logging
    "setup_logging",
    "get_logger",
    
    # Exceptions
    "RAGSystemException",
    "DocumentProcessingError",
    "EmbeddingGenerationError",
    "RetrievalError",
    "GenerationError",
    "ValidationError",
    "RateLimitExceeded",
    "CacheError",
]
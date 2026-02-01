"""
Enterprise Knowledge Assistant - RAG System

A production-ready Retrieval Augmented Generation system for querying
enterprise documents with grounded, validated responses.
"""

__version__ = "1.0.0"
__author__ = "Enterprise AI Team"
__license__ = "MIT"

from .core.config import get_settings
from .core.logging import setup_logging, get_logger

# Initialize logging on package import
settings = get_settings()
setup_logging(settings.LOG_LEVEL)

__all__ = [
    "get_settings",
    "setup_logging",
    "get_logger",
]
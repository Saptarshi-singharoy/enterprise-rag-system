class RAGSystemException(Exception):
    """Base exception for RAG system"""
    pass


class DocumentProcessingError(RAGSystemException):
    """Raised when document processing fails"""
    pass


class EmbeddingGenerationError(RAGSystemException):
    """Raised when embedding generation fails"""
    pass


class RetrievalError(RAGSystemException):
    """Raised when retrieval fails"""
    pass


class GenerationError(RAGSystemException):
    """Raised when LLM generation fails"""
    pass


class ValidationError(RAGSystemException):
    """Raised when response validation fails"""
    pass


class RateLimitExceeded(RAGSystemException):
    """Raised when rate limit is exceeded"""
    pass


class CacheError(RAGSystemException):
    """Raised when cache operation fails"""
    pass

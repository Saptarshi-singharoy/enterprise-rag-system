from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any
from datetime import datetime

class QueryRequest(BaseModel):
    """Request model for query endpoint"""
    query: str = Field(..., min_length=3, max_length=500)
    top_k: Optional[int] = Field(default=5, ge=1, le=20)
    include_sources: bool = Field(default=True)
    filters: Optional[Dict[str, Any]] = Field(default=None)

    @field_validator('query')
    def validate_query(cls, v):
        if not v.strip():
            raise ValueError("Query cannot be empty")
        return v.strip()
    

class Source(BaseModel):
    """Source document information"""
    file_name: str
    source: str
    chunk_index: int
    relevance_score: float

class QueryResponse(BaseModel):
    """Response model for query endpoint"""
    request_id: str
    query: str
    answer: str
    sources: Optional[List[Source]] = None
    context_docs_count: int
    grounding_score: float
    quality_score: float
    warnings: List[str] = []
    processing_time_ms: float
    timestamp: datetime


class DocumentUploadRequest(BaseModel):
    """Request model for document upload"""
    metadata: Optional[Dict[str, Any]] = None


class DocumentUploadResponse(BaseModel):
    """Response model for document upload"""
    document_id: str
    file_name: str
    chunks_created: int
    status: str
    message: str


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    timestamp: datetime
    components: Dict[str, str]




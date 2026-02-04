from fastapi import APIRouter, UploadFile, File, HTTPException,Depends
from fastapi.responses import JSONResponse
from typing import Optional
import uuid
import time
from pathlib import Path
import tempfile
from datetime import datetime

from .models import (
    QueryRequest,
    QueryResponse,
    DocumentUploadResponse,
    HealthResponse,
    Source
)

from ..ingestion.document_processor import DocumentProcessor
from ..ingestion.metadata_enricher import MetadataEnricher
from ..retrieval.vector_store import get_vector_store
from ..generation.llm_chain import RAGChain
from ..generation.validator import ResponseValidator
from ..core.config import get_settings
from ..core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()

router = APIRouter()

# Initialize components
doc_processor = DocumentProcessor()
metadata_enricher = MetadataEnricher()
vector_store = get_vector_store()
rag_chain = RAGChain()
validator = ResponseValidator()

@router.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """
    Query enterprise documents using RAG
    
    This endpoint:
    1. Retrieves relevant document chunks
    2. Generates grounded response using LLM
    3. Validates response quality
    4. Returns answer with source attribution
    """
    request_id = str(uuid.uuid4())
    start_time= time.time()

    try:
        logger.info(f"Processing query: {request.query}", extra={"request_id": request_id})
        
        # Retrieve relevant documents
        context_docs = await vector_store.similarity_search(
            query=request.query,
            k=request.top_k,
            filter=request.filters or None
        )

        if not context_docs:
            raise HTTPException(
                status_code=404,
                detail="No relevant documents found"
            )
        
        # Generate Response
        response = await rag_chain.generate_response(
            query=request.query,
            context_docs=context_docs,
            include_sources=request.include_sources
        )

        # Validate Response
        validation_result = validator.validate(response, context_docs)

        # Calculate processing time
        processing_time_ms = (time.time() - start_time) * 1000

        # Build Response
        sources = None
        if request.include_sources and "sources" in response:
            sources = [Source(**s) for s in response["sources"]]

        return QueryResponse(
            request_id=request_id,
            query=request.query,
            answer=response["answer"],
            sources=sources,
            context_docs_count=len(context_docs),
            grounding_score=validation_result["grounding_score"],
            quality_score=validation_result["quality_score"],
            warnings=validation_result["warnings"],
            processing_time_ms=processing_time_ms,
            timestamp=datetime.now()
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Query failed: {str(e)}", extra={"request_id":request_id})
        raise HTTPException(status_code=500, detail=str(e))

@router.post('/documents/upload', response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    metadata: Optional[str] = None
):
    """
    Upload and process a document
    
    This endpoint:
    1. Validates and saves the file
    2. Processes and chunks the document
    3. Generates embeddings
    4. Stores in vector database
    """
    try:
        # Validate File type
        file_suffix = Path(file.filename).suffix
        if file_suffix not in settings.SUPPORTED_FORMATS:
            raise HTTPException(
                status_code=400,
                details=f"Unsupported file format: {file_suffix}"
            )
        
        # Save to temporary location
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=file_suffix
        ) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = Path(tmp_file.name)

        # Process Document
        custom_metadata = eval(metadata) if metadata else {}
        chunks = doc_processor.process_document(
            tmp_path, custom_metadata
        )

        # Enrich metadata
        enriched_chunks = [
            metadata_enricher.enrich(chunk) for chunk in chunks
        ]

        # Add to vector store
        doc_ids = await vector_store.add_documents(
            enriched_chunks
        )

        # Cleanup
        tmp_path.unlink()

        logger.info(f"Document uploaded: {file.filename}, {len(chunks)} chunks")

        return DocumentUploadResponse(
            document_id=doc_ids[0] if doc_ids else str(uuid.uuid4()),
            file_name=file.filename,
            chunks_created=len(chunks),
            status="success",
            message=f"Document processed successfully with {len(chunks)} chunks"
        )
    except Exception as e:
        logger.error(f"Upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get('/health', response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        version=settings.VERSION,
        timestamp=datetime.now(),
        components={
            "api": "operational",
            "vector_store": "operational",
            "llm": "operational"
        }
    )
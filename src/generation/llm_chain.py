from typing import List, Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain_classic.prompts import PromptTemplate
from langchain_classic.schema import Document

from ..core.config import get_settings
from ..core.logging import get_logger
from ..core.exceptions import GenerationError

logger = get_logger(__name__)
settings = get_settings()

class RAGChain:
    """Manages the RAG pipeline with LLM"""

    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=settings.OPENAI_TEMPERATURE,
            max_completion_tokens=settings.OPENAI_MAX_TOKENS,
            openai_api_key=settings.OPENAI_API_KEY
        )

        self.prompt_template = self._create_prompt_template()

    def _create_prompt_template(self) -> PromptTemplate:
        """Create prompt template for RAG"""
        template = """You are an expert assistant helping users find information from enterprise documents.
        Use the following context to answer the question. If you cannot find the answer in the context, say so clearly.
        Context:
        {context}
        Question: {question}
        Instructions:
        1. Answer based ONLY on the provided context
        2. Cite specific sources when possible
        3. If information is not in context, state: "I don't have enough information to answer this question based on the available documents."
        4. Be concise but comprehensive
        5. Include relevant quotes from source documents
        Answer:"""
        
        return PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )
    
    async def generate_response(
            self,
            query:str,
            context_docs: List[Document],
            include_sources: bool = True
    ) -> Dict[str, Any]:
        """
        Generate response using RAG pipeline
        
        Args:
            query: User question
            context_docs: Retrieved context documents
            include_sources: Whether to include source attribution
            
        Returns:
            Response with answer and metadata
        """
        try:
            # Format context
            context = self._format_context(context_docs)

            # Generate Response
            prompt = self.prompt_template.format(
                context,
                question=query
            )

            response = await self.llm.invoke(prompt)
            answer = response.content

            # Build response object
            result = {
                "answer": answer,
                "query": query,
                "model": settings.OPENAI_MODEL,
                "context_docs_count": len(context_docs)
            }
            if include_sources:
                result["sources"] = self._extract_sources(context_docs)

            logger.info(f"Generated response for query: {query[:50]}...")
            return result
            
        except Exception as e:
            logger.error(f"Generation failed: {str(e)}")
            raise GenerationError(f"Response generation failed: {str(e)}") from e



    
    def _format_context(self, docs: List[Document])-> str:
        """Format context document for prompts"""
        formatted = []
        for i, doc in enumerate(docs, 1):
            source = doc.metadata.get("source", "Unknown")
            content = doc.page_content
            formatted.append(f"Document {i} - {source}\n{content}\n")

        return "\n".join(formatted)
    
    def _extract_sources(self, docs: List[Document]) -> List[Dict[str, Any]]:
        """Extract source information from documents"""
        sources = []

        for doc in docs:
            sources.append({
                "file_name": doc.metadata.get("file_name", "Unknown"),
                "source": doc.metadata.get("source", "Unknown"),
                "chunk_index": doc.metadata.get("chunk_index", 0),
                "relevance_score": doc.metadata.get("relevance_score", 0.0),
            })
        return sources
    
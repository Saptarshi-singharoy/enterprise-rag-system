from typing import Dict, Any, List
import re
from datetime import datetime

from langchain_classic.schema import Document
from ..core.logging import get_logger

logger = get_logger(__name__)

class MetadataEnricher:
    """Extract and enrich document metadata"""

    def __init__(self):
        self.entity_patters = {
            "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            "phone": r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            "date": r'\b\d{1,2}/\d{1,2}/\d{2,4}\b',
            "url": r'https?://[^\s]+',
        }
    
    def enrich(self, document: Document) -> Document:
        """Extract additional metadata from document content"""

        content = document.page_content

        # EExtract entities
        entities = self._extract_entities(content)

        # Calculate Statistics
        stats = self._calculate_statistics(content)

        # Identify content type
        content_type = self._identify_content_type(document)

        document.metadata.update({
            "entities": entities,
            "statistics": stats,
            "content_type": content_type,
            "enriched_at": datetime.now().isoformat(),
        })

        return document
    
    def _extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract entities using regex pattern"""
        entities={}

        for entity_type, pattern in self.entity_patters.items():
            matches = re.findall(pattern, text)
            if matches:
                entities[entity_type] = list(set(matches))

        return entities
    
    def _calculate_statistics(self, text: str) -> Dict[str, int]:
        """Calculate text statistics"""
        return {
            "char_count": len(text),
            "word_count": len(text.split()),
            "sentence_count": len(re.split(r'[.!?]+', text)),
            "paragraph_count": len(text.split('\n\n')),
        }
    
    def _identify_content_type(self, document: Document) -> str:
        """Identify content type based on patterns"""
        content = document.page_content.lower()
        
        if any(word in content for word in ["class", "def ", "function", "import"]):
            return "code"
        elif any(word in content for word in ["abstract", "introduction", "methodology"]):
            return "academic"
        elif "meeting" in content or "agenda" in content:
            return "meeting_notes"
        elif "policy" in content or "procedure" in content:
            return "policy"
        else:
            return "general"

from typing import Dict, Any, List
import re

from ..core.logging import get_logger
from ..core.exceptions import ValidationError

logger = get_logger(__name__)

class ResponseValidator:
    """Validates LLM responses for quality and safety"""
    def __init__(self):
        self.min_answer_length = 10
        self.max_answer_length = 5000

        # Patterns indicating hallucination or uncertainty
        self.uncertainty_phrases = [
            "i don't have enough information",
            "cannot find",
            "not available in the context",
            "not mentioned in the documents",
        ]

    def validate(
            self,
            response: Dict[str, Any],
            context_docs: List[Any]
    ) -> Dict[str, Any]:
        """
        Validate response quality and grounding
        
        Args:
            response: Generated response
            context_docs: Context documents used
            
        Returns:
            Validation result with flags and metadata
        """
        answer = response.get("answer","")

        validation_result = {
            "is_valid":True,
            "warnings":[],
            "grounding_score":0.0,
            "quality_score":0.0
        }

        if len(answer) < self.min_answer_length:
            validation_result["warnings"].append("Answer too short")
            validation_result["quality_score"] -= 0.2

        if len(answer) > self.max_answer_length:
            validation_result["warnings"].append("Answer too long")
            validation_result["quality_score"] -= 0.1

        # Check grounding
        grounding_score = self._check_grounding(answer, context_docs)
        validation_result["grounding_score"] = grounding_score

        if grounding_score < 0.5:
            validation_result["warnings"].append("Low grounding score")

        # Check for uncertainity
        if self._contains_uncertainity(answer):
            validation_result["warnings"].append("Response indicates uncertainity")

        # Calculate overall quality
        validation_result["quality_score"] = self._calculate_quality_score(answer, grounding_score)

        logger.info(f"Validation complete {validation_result}")
        return validation_result
    
    def _check_grounding(
            self,
            answer: str,
            context_docs: List[Any]
    ) -> float:
        """Check how well answer is grounded in context"""
        if not context_docs:
            return 0.0
        
        # Extract key phrases from answer
        answer_lower = answer.lower()

        overlap_count = 0
        total_terms = 0

        for doc in context_docs:
            context_lower = doc.page_content.lower()

            # Simple word overlap check
            answer_words = set(re.findall(r'\w+', answer_lower))
            context_words = set(re.findall(r'\w+', context_lower))

            overlap_count += len(answer_words & context_words)
            total_terms += len(answer_words)

        if total_terms == 0:
            return 0.0
        return min(overlap_count/ total_terms, 1.0)
    
    def _contains_uncertainity(self, answer: str) -> bool:
        """Check if answer contains uncertainty phrases"""
        answer_lower = answer.lower()
        return any(phrase in answer_lower for phrase in self.uncertainty_phrases)
    
    def _calculate_quality_score(
            self, answer: str, grounded_score: float
    ) -> float:
        """Calculate overall quality score"""

        score = grounded_score

        word_count = len(answer.split())
        if 50 <= word_count <= 500:
            score += 0.2


        if word_count < 20 or word_count > 1000:
            score -= 0.3

        return max(0.0, min(1.0, score))
    


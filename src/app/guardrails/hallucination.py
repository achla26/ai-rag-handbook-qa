from typing import List
from dataclasses import dataclass 

from src.app.core.embeddings import embedding_service
from src.utils.logger import logger


@dataclass
class HallucinationResult:
    """Hallucination check result."""
    is_grounded: bool
    groundedness_score: float
    flagged_sentences: List[str]
    details: str


class HallucinationDetector: 
    """Check if answers are grounded on sources or LLM generate it"""
    def __init__(self, threshold: float = 0.5):
        self.embedder = embedding_service
        self.threshold = threshold
    
    def _split_sentences(self, text: str) -> List[str]:
        """Text ko sentences mein split karo."""
        import re
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip() and len(s) > 10]
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Do texts ki similarity score."""
        return self.embedder.similarity(text1, text2)
    
    def check(
        self,
        answer: str,
        context: str
    ) -> HallucinationResult:
        """Verify answer against context."""
        
        # Skip generic responses
        skip_phrases = [
            "i don't have enough information",
            "i don't know",
            "cannot answer",
            "no information"
        ]
        
        if any(phrase in answer.lower() for phrase in skip_phrases):
            return HallucinationResult(
                is_grounded=True,
                groundedness_score=1.0,
                flagged_sentences=[],
                details="✅ Appropriate refusal - no hallucination check needed"
            )
        
        # Split answer into sentences
        sentences = self._split_sentences(answer)
        
        if not sentences:
            return HallucinationResult(
                is_grounded=True,
                groundedness_score=1.0,
                flagged_sentences=[],
                details="✅ No sentences to check"
            )
        
        # Check each sentence against context
        flagged = []
        scores = []
        
        for sentence in sentences:
            # Remove citation markers for comparison
            import re
            clean_sentence = re.sub(r'\[Source\s*\d+\]', '', sentence).strip()
            
            if len(clean_sentence) < 10:
                continue
            
            similarity = self._calculate_similarity(clean_sentence, context)
            scores.append(similarity)
            
            if similarity < self.threshold:
                flagged.append(f"'{clean_sentence}' (score: {similarity:.2f})")
        
        # Calculate overall groundedness
        avg_score = sum(scores) / len(scores) if scores else 1.0
        is_grounded = len(flagged) == 0
        
        if is_grounded:
            details = f"✅ All sentences grounded (avg score: {avg_score:.2f})"
        else:
            details = f"⚠️ {len(flagged)} sentence(s) may be hallucinated"
        
        return HallucinationResult(
            is_grounded=is_grounded,
            groundedness_score=round(avg_score, 3),
            flagged_sentences=flagged,
            details=details
        )


# Singleton
hallucination_detector = HallucinationDetector()
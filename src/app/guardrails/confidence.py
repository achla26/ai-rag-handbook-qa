from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import logging

from src.config.settings import settings

logger = logging.getLogger(__name__)


@dataclass
class ConfidenceResult:
    """Confidence assessment result."""
    should_answer: bool
    confidence_level: str  # HIGH, MEDIUM, LOW
    avg_score: float
    reason: str


class ConfidenceScorer:
    """Decide have to give answer or abstain."""
    
    def __init__(
        self,
        high_threshold: float = 0.6,
        low_threshold: float = 0.3
    ):
        self.high_threshold = high_threshold
        self.low_threshold = low_threshold
    
    def assess(
        self,
        sources: List[Dict[str, Any]],
        min_sources: int = 1
    ) -> ConfidenceResult:
        """Decide confidence from Sources scores."""
        
        # No sources found
        if not sources:
            return ConfidenceResult(
                should_answer=False,
                confidence_level="LOW",
                avg_score=0.0,
                reason="No relevant sources found"
            )
        
        # Calculate average score
        scores = [src["score"] for src in sources]
        avg_score = sum(scores) / len(scores)
        max_score = max(scores)
        
        # Not enough sources
        if len(sources) < min_sources:
            return ConfidenceResult(
                should_answer=False,
                confidence_level="LOW",
                avg_score=avg_score,
                reason=f"Only {len(sources)} source(s), need {min_sources}"
            )
        
        # High confidence
        if max_score >= self.high_threshold:
            return ConfidenceResult(
                should_answer=True,
                confidence_level="HIGH",
                avg_score=avg_score,
                reason=f"High confidence (best: {max_score:.2f})"
            )
        
        # Medium confidence
        if max_score >= self.low_threshold:
            return ConfidenceResult(
                should_answer=True,
                confidence_level="MEDIUM",
                avg_score=avg_score,
                reason=f" confidence (best: {max_score:.2f})"
            )
        
        # Low confidence - don't answer
        return ConfidenceResult(
            should_answer=False,
            confidence_level="LOW",
            avg_score=avg_score,
            reason=f"Low confidence (best: {max_score:.2f}) - abstaining"
        )


# Singleton
confidence_scorer = ConfidenceScorer()
import re
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass

from src.utils.logger import logger



@dataclass
class CitationResult:
    """Citation validation result."""
    is_valid: bool
    total_citations: int
    valid_citations: int
    invalid_citations: List[int]
    details: str


class CitationValidator:
    """Check valid or fake citations """
    
    def __init__(self):
        self.citation_pattern = r'\[Source\s*(\d+)\]'
    
    def extract_citations(self, answer: str) -> List[int]:
        """Get all citations from Answer."""
        matches = re.findall(self.citation_pattern, answer, re.IGNORECASE)
        return [int(m) for m in matches]
    
    def validate(
        self,
        answer: str,
        sources: List[Dict[str, Any]]
    ) -> CitationResult:
        """Check each citation is point to valid source ."""
        
        # Extract citations from answer
        cited_ids = self.extract_citations(answer)
        
        if not cited_ids:
            # No citations found
            return CitationResult(
                is_valid=False,
                total_citations=0,
                valid_citations=0,
                invalid_citations=[],
                details="⚠️ No citations found in answer"
            )
        
        # Valid source IDs
        valid_source_ids = {src["id"] for src in sources}
        
        # Check each citation
        valid_count = 0
        invalid_ids = []
        
        for cite_id in cited_ids:
            if cite_id in valid_source_ids:
                valid_count += 1
            else:
                invalid_ids.append(cite_id)
        
        # Unique invalid
        invalid_ids = list(set(invalid_ids))
        
        is_valid = len(invalid_ids) == 0 and valid_count > 0
        
        if is_valid:
            details = f"✅ All {valid_count} citations are valid"
        else:
            details = f"❌ Invalid citations: {invalid_ids}"
        
        return CitationResult(
            is_valid=is_valid,
            total_citations=len(cited_ids),
            valid_citations=valid_count,
            invalid_citations=invalid_ids,
            details=details
        )
    
    def get_cited_content(
        self,
        answer: str,
        sources: List[Dict[str, Any]],
        chunks: List[Any]
    ) -> Dict[int, str]:
        """fetch actual content of Cited sources."""
        
        cited_ids = set(self.extract_citations(answer))
        cited_content = {}
        
        for src in sources:
            if src["id"] in cited_ids:
                # Find matching chunk
                for chunk in chunks:
                    if chunk.chunk_id == src["chunk_id"]:
                        cited_content[src["id"]] = chunk.content
                        break
        
        return cited_content


# Singleton
citation_validator = CitationValidator()
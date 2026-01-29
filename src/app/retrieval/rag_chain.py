from typing import Dict, Any, Optional 
from dataclasses import dataclass 

from src.app.retrieval.retriever import retriever
from src.app.core.llm import llm_client
from src.app.guardrails.citation_validator import citation_validator
from src.app.guardrails.hallucination import hallucination_detector
from src.app.guardrails.confidence import confidence_scorer
from src.utils.logger import logger


SYSTEM_PROMPT = """You are a helpful assistant that answers questions based ONLY on the provided sources.

RULES:
1. ONLY use information from the provided sources
2. ALWAYS cite your sources using [Source X] format
3. If sources don't contain the answer, say "I don't have enough information to answer this question"
4. Be concise and accurate
5. Never make up information"""

USER_PROMPT_TEMPLATE = """Sources:
{context}

---

Question: {query}

Answer the question using ONLY the sources above. Include [Source X] citations."""


@dataclass
class RAGResponse:
    """RAG response with guardrail checks."""
    question: str
    answer: str
    sources: list
    
    # Guardrail results
    confidence_level: str
    citations_valid: bool
    is_grounded: bool
    
    # Metadata
    should_answer: bool
    warnings: list
    latency: float
    usage: dict


class RAGChain:
    """Production-grade RAG with guardrails."""
    
    def __init__(self):
        self.retriever = retriever
        self.llm = llm_client
        self.citation_validator = citation_validator
        self.hallucination_detector = hallucination_detector
        self.confidence_scorer = confidence_scorer
    
    def query(
        self,
        question: str,
        top_k: Optional[int] = None
    ) -> RAGResponse:
        """Answer of Question with citations."""
        
        warnings = []
        
        # Step 1: Retrieve relevant chunks
        retrieval_result = self.retriever.retrieve_with_context(
            query=question,
            top_k=top_k
        )
        
        sources = retrieval_result["sources"]
        context = retrieval_result["context"]
        chunks = retrieval_result["chunks"]
        
        # Step 2: Confidence check - should we even answer?
        confidence = self.confidence_scorer.assess(sources)
        
        if not confidence.should_answer:
            return RAGResponse(
                question=question,
                answer="I don't have enough information to answer this question.",
                sources=sources,
                confidence_level=confidence.confidence_level,
                citations_valid=True,
                is_grounded=True,
                should_answer=False,
                warnings=[confidence.reason],
                latency=0.0,
                usage={}
            )
        
        if confidence.confidence_level == "MEDIUM":
            warnings.append(f"⚠️ Medium confidence: {confidence.reason}")
        
        # Step 3: Generate answer
        user_prompt = USER_PROMPT_TEMPLATE.format(
            context=context,
            query=question
        )
        
        response = self.llm.generate(
            prompt=user_prompt,
            system_prompt=SYSTEM_PROMPT
        )
        
        answer = response["content"]
        
        # Step 4: Validate citations
        citation_result = self.citation_validator.validate(answer, sources)
        
        if not citation_result.is_valid:
            warnings.append(f"⚠️ Citation issue: {citation_result.details}")
        
        # Step 5: Hallucination check
        hallucination_result = self.hallucination_detector.check(answer, context)
        
        if not hallucination_result.is_grounded:
            warnings.append(f"⚠️ Grounding issue: {hallucination_result.details}")
            for flagged in hallucination_result.flagged_sentences[:2]:
                warnings.append(f"   Flagged: {flagged}")
        
        return RAGResponse(
            question=question,
            answer=answer,
            sources=sources,
            confidence_level=confidence.confidence_level,
            citations_valid=citation_result.is_valid,
            is_grounded=hallucination_result.is_grounded,
            should_answer=True,
            warnings=warnings,
            latency=response["latency_seconds"],
            usage=response["usage"]
        )


# Singleton
rag_chain = RAGChain()
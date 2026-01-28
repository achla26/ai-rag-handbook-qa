from typing import Dict, Any, Optional 

from src.app.retrieval.retriever import retriever
from src.app.core.llm import llm_client
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


class RAGChain:
    """Retrieval Augmented Generation with citations."""
    
    def __init__(self):
        self.retriever = retriever
        self.llm = llm_client
    
    def query(
        self,
        question: str,
        top_k: Optional[int] = None
    ) -> Dict[str, Any]:
        """Answer of Question with citations."""
        
        # Step 1: Retrieve relevant chunks
        retrieval_result = self.retriever.retrieve_with_context(
            query=question,
            top_k=top_k
        )
        
        # Step 2: Check if context found
        if not retrieval_result["context"]:
            return {
                "question": question,
                "answer": "I don't have enough information to answer this question.",
                "sources": [],
                "has_answer": False
            }
        
        # Step 3: Build prompt
        user_prompt = USER_PROMPT_TEMPLATE.format(
            context=retrieval_result["context"],
            query=question
        )
        
        # Step 4: Generate answer
        response = self.llm.generate(
            prompt=user_prompt,
            system_prompt=SYSTEM_PROMPT
        )
        
        return {
            "question": question,
            "answer": response["content"],
            "sources": retrieval_result["sources"],
            "has_answer": True,
            "usage": response["usage"],
            "latency": response["latency_seconds"]
        }


# Singleton
rag_chain = RAGChain()
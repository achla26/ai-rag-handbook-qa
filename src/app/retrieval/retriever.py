from typing import List, Dict, Any, Optional
from dataclasses import dataclass


from src.config.settings import settings
from src.app.core.embeddings import embedding_service
from src.app.core.vector_store import vector_store
from src.utils.logger import logger , fprint 


@dataclass
class RetrievedChunk:
    """Retrieved chunk with score."""
    content: str
    score: float
    metadata: Dict[str, Any]
    chunk_id: str


class Retriever:
    """fetch relevant chunks Query."""
    
    def __init__(self):
        self.embedder = embedding_service
        self.vector_store = vector_store
        self.top_k = settings.top_k
        self.threshold = settings.similarity_threshold
    
    def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        threshold: Optional[float] = None
    ) -> List[RetrievedChunk]:
        """for Query fetch relevant chunks."""
        
        top_k = top_k or self.top_k
        threshold = threshold or self.threshold
        
        # Embed Query
        query_embedding = self.embedder.embed_query(query)
        
        # Search in DB
        results = self.vector_store.client.query_points(
            collection_name=settings.qdrant_collection_name,
            query=query_embedding,
            limit=self.top_k
        ) 

        # Convert to RetrievedChunk
        chunks = []
        for result in results.points: 
            chunk = RetrievedChunk(
                content=result.payload.get("content", ""),
                score=result.score,
                metadata={
                    "source": result.payload.get("source", ""),
                    "chunk_index": result.payload.get("chunk_index", 0),
                    "doc_id": result.payload.get("doc_id", "")
                },
                chunk_id=result.payload.get("chunk_id", "")
            )
            chunks.append(chunk)
        
        logger.info(f"Query: '{query[:50]}...' → {len(chunks)} chunks found")
        return chunks 
    
    def retrieve_with_context(
        self,
        query: str,
        top_k: Optional[int] = None
    ) -> Dict[str, Any]:
        """Retrieve + formatted context for LLM."""
        
        chunks = self.retrieve(query, top_k)
        
        if not chunks:
            return {
                "query": query,
                "context": "",
                "chunks": [],
                "sources": []
            }
        
        # Context format karo with source numbers
        context_parts = []
        sources = []
        
        for idx, chunk in enumerate(chunks, 1):
            context_parts.append(f"[Source {idx}]: {chunk.content}")
            sources.append({
                "id": idx,
                "source": chunk.metadata["source"],
                "score": round(chunk.score, 4),
                "chunk_id": chunk.chunk_id
            })
        
        return {
            "query": query,
            "context": "\n\n".join(context_parts),
            "chunks": chunks,  # Return RetrievedChunk objects
            "sources": sources
        }
# Singleton
retriever = Retriever()
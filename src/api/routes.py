from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from src.api.schemas import (
    QueryRequest, QueryResponse,
    IngestRequest, IngestResponse,
    HealthResponse, SourceInfo, GuardrailInfo
)
from src.app.retrieval.rag_chain import rag_chain
from src.app.ingestion.pipeline import ingestion_pipeline
from src.app.core.vector_store import vector_store
from src.app.core.llm import llm_client
from src.utils.logger import logger 


router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Check all components health."""
    
    components = {}
    
    # Qdrant check
    qdrant_health = vector_store.health_check()
    components["qdrant"] = qdrant_health
    
    # LLM check
    llm_health = llm_client.health_check()
    components["llm"] = llm_health
    
    # Overall status
    all_healthy = (
        qdrant_health.get("status") == "healthy" and
        llm_health.get("status") == "healthy"
    )
    
    return HealthResponse(
        status="healthy" if all_healthy else "degraded",
        components=components
    )


@router.post("/ingest", response_model=IngestResponse)
async def ingest_documents(request: IngestRequest = None):
    """ingest Documents (load → chunk → embed → store)."""
    
    try:
        data_dir = request.data_dir if request else None
        stats = ingestion_pipeline.run(data_dir=data_dir)
        
        return IngestResponse(
            success=len(stats["errors"]) == 0,
            documents_loaded=stats["documents_loaded"],
            chunks_created=stats["chunks_created"],
            vectors_stored=stats["vectors_stored"],
            errors=stats["errors"]
        )
        
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """Ask Question, get cited answer."""
    
    try:
        result = rag_chain.query(
            question=request.question,
            top_k=request.top_k
        )
        
        # Format sources
        sources = [
            SourceInfo(
                id=s["id"],
                source=s["source"],
                score=s["score"],
                chunk_id=s.get("chunk_id", "")
            )
            for s in result.sources
        ]
        
        # Format guardrails
        guardrails = GuardrailInfo(
            confidence_level=result.confidence_level,
            citations_valid=result.citations_valid,
            is_grounded=result.is_grounded,
            should_answer=result.should_answer,
            warnings=result.warnings
        )
        
        return QueryResponse(
            question=result.question,
            answer=result.answer,
            sources=sources,
            guardrails=guardrails,
            latency_seconds=result.latency,
            token_usage=result.usage or {}
        )
        
    except Exception as e:
        logger.error(f"Query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_stats() -> Dict[str, Any]:
    """Fetch Collection stats ."""
    
    try:
        info = vector_store.get_collection_info()
        return {
            "collection": info,
            "status": "ok"
        }
    except Exception as e:
        return {
            "error": str(e),
            "status": "error"
        }
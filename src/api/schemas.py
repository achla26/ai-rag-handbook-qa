from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


# ============ Request Models ============

class QueryRequest(BaseModel):
    """Request for asking Question."""
    question: str = Field(..., min_length=3, max_length=1000)
    top_k: Optional[int] = Field(5, ge=1, le=20)
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "How many annual leaves can I take?",
                "top_k": 5
            }
        }


class IngestRequest(BaseModel):
    """Request for Document ingest ."""
    data_dir: Optional[str] = Field(None, description="Custom data directory")


# ============ Response Models ============

class SourceInfo(BaseModel):
    """Source document info."""
    id: int
    source: str
    score: float
    chunk_id: str


class GuardrailInfo(BaseModel):
    """Guardrail check results."""
    confidence_level: str
    citations_valid: bool
    is_grounded: bool
    should_answer: bool
    warnings: List[str]


class QueryResponse(BaseModel):
    """Response for Query with guardrails."""
    question: str
    answer: str
    sources: List[SourceInfo]
    guardrails: GuardrailInfo
    latency_seconds: float
    token_usage: Dict[str, int]
    timestamp: datetime = Field(default_factory=datetime.now)


class IngestResponse(BaseModel):
    """Ingestion pipeline result."""
    success: bool
    documents_loaded: int
    chunks_created: int
    vectors_stored: int
    errors: List[str]
    timestamp: datetime = Field(default_factory=datetime.now)


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    components: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.now)
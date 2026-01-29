from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import router

# FastAPI app
app = FastAPI(
    title="Handbook Q&A API",
    description="Production-grade RAG with citations and guardrails",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "message": "Handbook Q&A API",
        "docs": "/docs",
        "health": "/api/v1/health"
    }
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, SecretStr
from typing import Literal

class Settings(BaseSettings):
    """Application configuration with environment variable support."""
    
    # API Keys (SecretStr for security : won't print API keys in logs)
    groq_api_key: SecretStr = Field(
        ...,
        description="Groq API Key for LLM access",
        examples=["sk-..."]
    )
    
    # Qdrant Configuration
    qdrant_url: str = Field(
        "http://localhost:6333",
        description="Qdrant server URL with protocol",
        examples=["http://localhost:6333", "http://qdrant:6333"]
    )
    
    qdrant_collection_name: str = Field(
        "handbook_qa",
        description="Collection name for vector storage",
        pattern=r"^[a-zA-Z0-9_-]+$"  # Valid collection name pattern
    )
    
    # Embedding Model
    embedding_model: str = Field(
        "sentence-transformers/all-MiniLM-L6-v2",
        description="Hugging Face model for embeddings"
    )
    
    embedding_dimension: int = Field(
        384,  
        description="Dimension of embedding vectors",
        gt=0
    )
    
    # Text Processing
    max_chunk_size: int = Field(
        1000,
        description="Maximum chunk size in characters",
        gt=0,
        le=10000
    )
    
    chunk_overlap: int = Field(
        200,
        description="Chunk overlap in characters",
        ge=0,
        lt=1000
    )
    
    # Retrieval Parameters
    top_k: int = Field(
        5,
        description="Number of chunks to retrieve",
        gt=0,
        le=20
    )
    
    similarity_threshold: float = Field(
        0.7,
        description="Minimum similarity score for retrieval",
        ge=0.0,
        le=1.0
    )
    
    # LLM Configuration
    llm_model: str = Field(
        "llama-3.3-70b-versatile",
        description="Groq model identifier"
    )
    
    llm_temperature: float = Field(
        0.1,
        description="Temperature for LLM generation",
        ge=0.0,
        le=2.0
    )
    
    llm_max_tokens: int = Field(
        1024,
        description="Maximum tokens for LLM response",
        gt=0,
        le=8192
    )
    
    # Application Settings
    debug: bool = Field(
        False,
        description="Enable debug mode with verbose logging"
    )
    
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(
        "INFO",
        description="Application log level"
    )
    
    # Pydantic v2 Configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        # env_prefix="APP_",  # Optional: prefix for env vars
        case_sensitive=False,
        extra="ignore",
        validate_default=True
    )


# Singleton instance with error handling
try:
    settings = Settings()
except Exception as e:
    import sys
    print(f"❌ Failed to load settings: {e}", file=sys.stderr)
    print("Create a .env file or set environment variables", file=sys.stderr)
    sys.exit(1)
 
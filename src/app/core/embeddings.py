from sentence_transformers import SentenceTransformer
from typing import List, Union
import numpy as np
import logging

from src.config.settings import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Local embedding service using Sentence Transformers."""
    
    def __init__(self):
        self._model = None  # Lazy loading
    
    @property
    def model(self) -> SentenceTransformer:
        """Lazy load model (saves memory on startup)."""
        if self._model is None:
            logger.info(f"Loading embedding model: {settings.embedding_model}")
            self._model = SentenceTransformer(settings.embedding_model)
            logger.info("Model loaded successfully")
        return self._model
    
    def embed_query(self, text: str) -> List[float]:
        """Embed Single query."""
        embedding = self.model.encode(text, normalize_embeddings=True)
        return embedding.tolist()
    
    def embed_documents(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """Multiple texts ko batch mein embed karo (faster)."""
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            normalize_embeddings=True,
            show_progress_bar=True
        )
        return embeddings.tolist()
    
    def similarity(self, text1: str, text2: str) -> float:
        """Do texts ke beech similarity score."""
        emb1 = np.array(self.embed_query(text1))
        emb2 = np.array(self.embed_query(text2))
        return float(np.dot(emb1, emb2))


# Singleton
embedding_service = EmbeddingService()

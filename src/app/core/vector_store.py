from qdrant_client import QdrantClient
from qdrant_client.http import models
from typing import List, Dict, Any


from src.config.settings import settings 
from src.utils.logger import logger

class VectorStore:
    """Qdrant Vector Database operations handler."""
    
    def __init__(self):
        self.client = QdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key.get_secret_value())
        self.collection_name = settings.qdrant_collection_name
        self.vector_size = settings.embedding_dimension
    
    def create_collection(self) -> bool:
        """Collection create if not exist."""
        try:
            exists =  self.client.collection_exists(collection_name={self.collection_name}) 
            
            if not exists:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=models.VectorParams(
                        size=self.vector_size,
                        distance=models.Distance.COSINE
                    )
                )
                logger.info(f"Collection '{self.collection_name}' created")
            else:
                logger.info(f"Collection '{self.collection_name}' already exists")
            
            return True
            
        except Exception as e:
            logger.error(f"Collection creation failed: {e}")
            raise
    
    def health_check(self) -> Dict[str, Any]:
        """Qdrant connection health check."""
        try:
            info = self.client.get_collections()
            return {
                "status": "healthy",
                "collections_count": len(info.collections),
                "url": settings.qdrant_url,
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    def get_collection_info(self , collection_name: str|None = None) -> Dict[str, Any]:
        """Fetch Collection details."""
        try: 
            collection_name = collection_name or self.collection_name
            info = self.client.get_collection(collection_name=self.collection_name)
           
            return {
                "name": self.collection_name,
                "vectors_count": info.indexed_vectors_count,
                "points_count": info.points_count,
                "status":info.status
            }
        except Exception as e:
            return {"error": f"Collection not found {e}"}

vector_store = VectorStore()
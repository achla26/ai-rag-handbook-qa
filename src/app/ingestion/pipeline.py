from typing import List, Dict, Any, Optional
from uuid import uuid4

from src.config.settings import settings
from src.app.ingestion.loader import document_loader, Document
from src.app.ingestion.chunker import text_chunker, Chunk
from src.app.core.embeddings import embedding_service
from src.app.core.vector_store import vector_store

from qdrant_client.http import models
from src.utils.logger import logger , fprint 

class IngestionPipeline:
    """Complete ingestion: Load → Chunk → Embed → Store."""
    
    def __init__(self):
        self.loader = document_loader
        self.chunker = text_chunker
        self.embedder = embedding_service
        self.vector_store = vector_store
        fprint('Instances Loaded Successfully.')

    def _prepare_points(self, chunks: List[Chunk]) -> List[models.PointStruct]:
        """Convert Chunks into Qdrant points ."""
        
        texts = [chunk.content for chunk in chunks]
        embeddings = self.embedder.embed_documents(texts)
        
        points = []
        for chunk, embedding in zip(chunks, embeddings):
            point = models.PointStruct(
                id=str(uuid4()),
                vector=embedding,
                payload={
                    "content": chunk.content,
                    "chunk_id": chunk.chunk_id,
                    "chunk_index": chunk.chunk_index,
                    **chunk.metadata
                }
            )
            points.append(point)
        
        return points
    
    def run(self, data_dir: Optional[str] = None) -> Dict[str, Any]:
        """Run Full pipeline."""
        
        stats = {
            "documents_loaded": 0,
            "chunks_created": 0,
            "vectors_stored": 0,
            "errors": []
        }
        
        try:
            # Step 1: Collection ready karo
            fprint("Preparing collection..." , True)
            self.vector_store.create_collection()
            
            # Step 2: Documents load karo
            fprint("Loading documents..." , True)
            if data_dir:
                self.loader.data_dir = data_dir

            documents = self.loader.load_directory()
            stats["documents_loaded"] = len(documents)
            
            if not documents:
                logger.warning("No documents found!")
                return stats
            
            # Step 3: Chunk karo
            fprint("Chunking documents..." , True)
            chunks = self.chunker.chunk_documents(documents)
            stats["chunks_created"] = len(chunks)
            
            # Step 4: Embed + Store karo
            fprint("Embedding and storing..." ,True)
            points = self._prepare_points(chunks)
            
            # Batch upsert (100 at a time)
            batch_size = 100
            for i in range(0, len(points), batch_size):
                batch = points[i:i + batch_size]
                self.vector_store.client.upsert(
                    collection_name=settings.qdrant_collection_name,
                    points=batch
                )
            
            stats["vectors_stored"] = len(points)
            
            fprint("Pipeline completed!" , True)
            logger.info(f"Stats: {stats}")
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            stats["errors"].append(str(e))
        
        return stats


# Singleton
ingestion_pipeline = IngestionPipeline()
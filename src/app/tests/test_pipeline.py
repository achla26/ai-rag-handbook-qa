from src.app.ingestion.pipeline import ingestion_pipeline
from src.utils.logger import logger , fprint 

def main():
    fprint("🚀 Running Ingestion Pipeline...") 
    
    stats = ingestion_pipeline.run()
    
    fprint("\n📊 Pipeline Results:")
    fprint(f"   Documents loaded: {stats['documents_loaded']}")
    fprint(f"   Chunks created: {stats['chunks_created']}")
    fprint(f"   Vectors stored: {stats['vectors_stored']}")
    
    if stats["errors"]:
        logger.error(f"   ❌ Errors: {stats['errors']}")
    else:
        logger.info("   ✅ No errors!")

if __name__ == "__main__":
    main()
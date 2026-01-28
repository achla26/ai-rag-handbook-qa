from src.app.core.vector_store import vector_store
from src.utils.logger import logger

# Health check
def main():
    logger.info("Health Check...")
    try:
        if vector_store.health_check():
            logger.info("Qdrant connected!")
            
            # Collection create
            vector_store.create_collection()
            logger.info("Collection ready!")
        else:
            logger.error("Qdrant connection failed - Docke!")

    except Exception as e:
        logger.error(f"Qdrant connection failed: {e}")
        raise


if __name__ == "__main__":
    main()
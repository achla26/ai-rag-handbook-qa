from src.app.ingestion.loader import document_loader
from src.app.ingestion.chunker import text_chunker
from src.utils.logger import logger
 
def main():
    # Load documents
    logger.info(f"Loading documents...") 
    documents = document_loader.load_directory()

    if not documents:
        logger.info("No documents found! Add files to data/documents/")
        return

    # Chunk documents
    logger.info("\nChunking documents...")
    chunks = text_chunker.chunk_documents(documents)

    # Display chunks
    logger.info(f"\nTotal chunks: {len(chunks)}")
    logger.info("-" * 50)

    for chunk in chunks[:5]:  # First 5 chunks
        logger.info(f"\nChunk ID: {chunk.chunk_id}")
        logger.info(f"   Index: {chunk.chunk_index}")
        logger.info(f"   Length: {len(chunk.content)} chars")
        logger.info(f"   Content: {chunk.content[:150]}...")

if __name__ == "__main__":
    main()
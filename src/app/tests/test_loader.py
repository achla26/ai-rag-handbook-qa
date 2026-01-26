from src.app.ingestion.loader import document_loader
from src.utils.logger import logger  
 
def main():
    logger.info("📂 Loading documents...")
    documents = document_loader.load_directory()

    if not documents:
        logger.info("No documents found! Add files to data/documents/")
        return
    
    for doc in documents:
        logger.info(f"\n📄 Document: {doc.metadata['source']}")
        logger.info(f"   ID: {doc.doc_id}")
        logger.info(f"   Length: {len(doc.content)} chars")
        logger.info(f"   Preview: {doc.content[:100]}...")
   

if __name__ == "__main__":
    main()
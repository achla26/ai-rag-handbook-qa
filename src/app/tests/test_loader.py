from src.app.ingestion.loader import document_loader
from src.utils.logger import logger , fprint
from src.utils.decorators import log_step
 

def main():
    fprint("Loading documents...")
    documents = document_loader.load_directory()

    if not documents:
        logger.error("No documents found! Add files to data/documents/")
        return
    
    for doc in documents:
        fprint(f"\n Document: {doc.metadata['source']}")
        fprint(f"   ID: {doc.doc_id}")
        fprint(f"   Length: {len(doc.content)} chars")
        fprint(f"   Preview: {doc.content[:100]}...")

if __name__ == "__main__":
    main()
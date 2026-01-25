from pathlib import Path
from typing import Dict, Any
from dataclasses import dataclass
import hashlib
import logging

logger = logging.getLogger(__name__)


@dataclass
class Document:
    """Loaded document ka structure."""
    content: str
    doc_id: str
    metadata: Dict[str, Any]

    @classmethod   
    def load_document(cls, content: str, file_path: Path, id: str) -> 'Document':
        return cls(
            content=content,
            metadata={
                "source": file_path.name,
                "file_path": str(file_path),
                "file_type": file_path.suffix
            },
            doc_id=id 
        )


 
class DocumentLoader:
    """Load documents from various formats"""
    
    SUPPORTED_EXTENSIONS = {".txt", ".md", ".pdf"}

    # create folder     
    def __init__(self, data_dir: str = "src/data/documents"):
        self.data_dir = Path(data_dir) 
        self.data_dir.mkdir(parents=True, exist_ok=True) 
    
    def _generate_doc_id(self, content: str, filename: str) -> str:
        """Unique document ID generate karo."""
        hash_input = f"{filename}:{content[:500]}" 
        return hashlib.md5(hash_input.encode()).hexdigest()[:12]

    def load_text_file(self, file_path: Path) -> Document:
        """Load TXT/MD file."""
        content = file_path.read_text(encoding="utf-8")

        doc_id=self._generate_doc_id(content, file_path.name)

        return Document.load_document(content , file_path , id =doc_id)       
 
    def load_file(self, file_path: Path) -> Document:
        """load Any supported file."""
        file_path = Path(file_path)
         
        if not file_path.exists(): 
            raise FileNotFoundError(f"File not found: {file_path}")
         
        
        if file_path.suffix not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(f"Unsupported file type: {file_path.suffix}")
        
        if file_path.suffix == ".pdf":
            pass
        else:
            return self.load_text_file(file_path)

 
loader = DocumentLoader()
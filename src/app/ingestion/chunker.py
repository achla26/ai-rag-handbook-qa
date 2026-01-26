from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import re
import logging
from pathlib import Path
import sys 

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

# from src.config.settings import settings
from src.app.ingestion.loader import Document
 

logger = logging.getLogger(__name__)

@dataclass
class Chunk:
    """Structure for a single chunk."""
    content: str
    metadata: Dict[str, Any]
    chunk_id: str
    chunk_index: int


class TextChunker:
    """Smart text chunking with semantic boundaries."""
    
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        separator: str = " "
    ):
        # Provide defaults if settings don't exist
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separator = separator
        
        # sentence split pattern based on look behind to match .!? in mid space and look ahead capital letter
        self.sentence_pattern = re.compile(r'(?<=[.!?])\s+(?=[A-Z])')
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences using regex."""
        sentences = self.sentence_pattern.split(text)
        # Clean and filter
        cleaned = [s.strip() for s in sentences if s.strip()]
        return cleaned
    
    def _merge_small_sentences(self, sentences: List[str], min_length: int = 50) -> List[str]:
        """Merge very short sentences to avoid tiny chunks."""
        if not sentences:
            return []
        
        merged = []
        current = sentences[0]
        
        for sentence in sentences[1:]:
            # If current is very short, merge with next
            if len(current) < min_length:
                current += self.separator + sentence
            else:
                merged.append(current)
                current = sentence
        
        merged.append(current)
        return merged
    
    def _split_long_sentence(self, sentence: str, max_length: int) -> List[str]:
        """Split a very long sentence by words.""" 
         
        if len(sentence) <= max_length:
            return [sentence]
        
        words = sentence.split(self.separator)
        parts = []
        current_part = []
        current_length = 0
    
        for word in words:
            # word_length should include separator only if not first word
            word_length = len(word) + (len(self.separator) if current_part else 0) 
            if current_length + word_length > max_length and current_part:
                parts.append(self.separator.join(current_part))
                current_part = [word]
                current_length = len(word)  # No separator for first word
            else:
                current_part.append(word)
                current_length += word_length
        
        if current_part:
            parts.append(self.separator.join(current_part))
        
        return parts

    def _create_chunks(self, sentences: List[str]) -> List[str]:
        """Create chunks from sentences with proper overlap."""
        if not sentences:
            return []
        
        chunks = []
        current_chunk = []
        current_length = 0
        
        i = 0
        while i < len(sentences):
            sentence = sentences[i]
            
            # Handle sentences longer than chunk_size
            if len(sentence) > self.chunk_size:
                sentence_parts = self._split_long_sentence(sentence, self.chunk_size)
                
                # Process each part
                for part in sentence_parts:
                    if current_length + len(part) > self.chunk_size and current_chunk:
                        chunks.append(self.separator.join(current_chunk))
                        
                        # Calculate overlap from previous chunk
                        if self.chunk_overlap > 0:
                            overlap_text = self.separator.join(current_chunk)
                            overlap_words = overlap_text.split(self.separator)
                            
                            # Take words from end for overlap
                            overlap_part = []
                            overlap_length = 0
                            for word in reversed(overlap_words):
                                if overlap_length + len(word) + len(self.separator) <= self.chunk_overlap:
                                    overlap_part.insert(0, word)
                                    overlap_length += len(word) + len(self.separator)
                                else:
                                    break
                            
                            if overlap_part:
                                current_chunk = overlap_part
                                current_length = overlap_length
                            else:
                                current_chunk = []
                                current_length = 0
                        else:
                            current_chunk = []
                            current_length = 0
                    
                    current_chunk.append(part)
                    current_length += len(part) + len(self.separator) if current_chunk else 0
                
                i += 1
                continue
            
            # Normal sentence processing
            if current_length + len(sentence) > self.chunk_size and current_chunk:
                chunks.append(self.separator.join(current_chunk))
                
                # Create overlap from current chunk
                if self.chunk_overlap > 0:
                    overlap_text = self.separator.join(current_chunk)
                    overlap_words = overlap_text.split(self.separator)
                    
                    # Take last few sentences for better semantic overlap
                    overlap_sentences = []
                    overlap_length = 0
                    
                    # Start from the last sentence in current chunk
                    for sent in reversed(current_chunk):
                        if overlap_length + len(sent) <= self.chunk_overlap:
                            overlap_sentences.insert(0, sent)
                            overlap_length += len(sent)
                        else:
                            break
                    
                    current_chunk = overlap_sentences
                    current_length = overlap_length
                else:
                    current_chunk = []
                    current_length = 0
            
            current_chunk.append(sentence)
            current_length += len(sentence) + len(self.separator) if len(current_chunk) > 1 else 0
            i += 1
        
        # Add the last chunk
        if current_chunk:
            chunks.append(self.separator.join(current_chunk))
        
        return chunks
    
    def chunk_document(self, document: 'Document') -> List[Chunk]:
        """Chunk a single document."""
        # Clean text
        text = document.content.strip()
        text = re.sub(r'\s+', self.separator, text)  # Normalize whitespace
        
        # Split into sentences
        sentences = self._split_into_sentences(text)
        
        # Merge very short sentences
        sentences = self._merge_small_sentences(sentences)
        
        # Create chunks
        chunk_texts = self._create_chunks(sentences)
        
        # Create Chunk objects
        chunks = []
        for idx, chunk_text in enumerate(chunk_texts):
            chunk = Chunk(
                content=chunk_text,
                metadata={
                    **document.metadata,
                    "doc_id": document.doc_id,
                    "chunk_index": idx,
                    "total_chunks": len(chunk_texts)
                },
                chunk_id=f"{document.doc_id}_{idx}",
                chunk_index=idx
            )
            chunks.append(chunk)
        
        logger.info(f"Document '{document.metadata.get('source', 'unknown')}' → {len(chunks)} chunks")
        return chunks
    
    def chunk_documents(self, documents: List['Document']) -> List[Chunk]:
        """Chunk multiple documents."""
        all_chunks = []
        
        for doc in documents:
            try:
                chunks = self.chunk_document(doc)
                all_chunks.extend(chunks)
            except Exception as e:
                logger.error(f"Failed to chunk document {doc.doc_id}: {str(e)}")
                # Continue with other documents
        
        logger.info(f"Total chunks created: {len(all_chunks)}")
        return all_chunks


# Optional singleton - better to instantiate with parameters
def create_chunker(
    chunk_size: int = 1000,
    chunk_overlap: int = 200
) -> TextChunker:
    """Factory function to create a chunker."""
    return TextChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)


text_chunker = create_chunker()
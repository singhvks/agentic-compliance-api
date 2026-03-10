import uuid
from typing import List, Dict

from app.core.config import settings
from app.models.domain_models import ChunkMetadata

class StaticChunker:
    """Chunks text into fixed sizes with overlap. Proxies tokens with word counts for simplicity without heavy dependencies."""
    
    def __init__(self, chunk_size: int = settings.CHUNK_SIZE, chunk_overlap: int = settings.CHUNK_OVERLAP):
        # Fallback to word counts to estimate tokens
        # 1 token ~ 0.75 words. So 800 tokens = ~600 words.
        self.word_chunk_size = int(chunk_size * 0.75)
        self.word_overlap = int(chunk_overlap * 0.75)
        
    def chunk_document(self, document_id: str, paginated_text: Dict[int, str]) -> List[ChunkMetadata]:
        chunks = []
        
        for page_num, text in paginated_text.items():
            words = text.split()
            
            if not words:
                continue
                
            i = 0
            while i < len(words):
                end = min(i + self.word_chunk_size, len(words))
                chunk_words = words[i:end]
                chunk_text = " ".join(chunk_words)
                
                chunk_id = str(uuid.uuid4())
                metadata = ChunkMetadata(
                    chunk_id=chunk_id,
                    document_id=document_id,
                    page_number=page_num,
                    text=chunk_text
                )
                chunks.append(metadata)
                
                if end == len(words):
                    break
                    
                i += (self.word_chunk_size - self.word_overlap)
                
        return chunks

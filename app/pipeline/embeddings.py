import numpy as np
from typing import List

from app.core.config import settings
from app.core.logging import logger

class EmbeddingsGenerator:
    """Generates embeddings using local sentence-transformers models."""
    
    def __init__(self, model_name: str = settings.EMBEDDING_MODEL):
        logger.info(f"Loading embedding model: {model_name}")
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(model_name)
        except ImportError:
            raise ImportError("sentence-transformers is required. Run 'pip install sentence-transformers'")
            
    def generate(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for a list of strings.
        Returns a numpy array of shape (len(texts), embedding_dim).
        """
        if not texts:
            return np.array([])
            
        logger.debug(f"Generating embeddings for {len(texts)} texts")
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings

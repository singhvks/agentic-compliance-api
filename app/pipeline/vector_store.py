import os
import faiss
import pickle
import numpy as np
from typing import List, Tuple
from pathlib import Path

from app.core.config import settings
from app.core.logging import logger
from app.models.domain_models import ChunkMetadata

class FAISSVectorStore:
    """Wrapper around FAISS to store and retrieve vectors and metadata."""
    
    def __init__(self, job_id: str):
        self.job_id = job_id
        self.base_dir = Path(settings.VECTOR_STORE_PATH) / job_id
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.index_path = str(self.base_dir / "index.faiss")
        self.meta_path = str(self.base_dir / "meta.pkl")
        
        # Will be lazy initialized
        self.index = None
        self.metadata_store: List[ChunkMetadata] = []
        
        self.embedding_dimension = 384 # Default for all-MiniLM-L6-v2
        
    def _init_index(self, dimension: int):
        if self.index is None:
            # We use a flat index for simplicity and precise exact search
            self.index = faiss.IndexFlatL2(dimension)
            self.embedding_dimension = dimension
            
    def add_embeddings(self, embeddings: np.ndarray, metadata: List[ChunkMetadata]) -> None:
        """
        Add generated embeddings and their metadata to the index.
        """
        if len(embeddings) == 0:
            return
            
        if len(embeddings) != len(metadata):
            raise ValueError(f"Embeddings length ({len(embeddings)}) does not match metadata length ({len(metadata)})")
            
        dim = embeddings.shape[1]
        self._init_index(dim)
        
        # Ensure it's the correct float type for FAISS
        embeddings = embeddings.astype(np.float32)
        
        self.index.add(embeddings)
        self.metadata_store.extend(metadata)
        
        logger.info("Added chunks to vector store", job_id=self.job_id, _count=len(metadata))
        
    def save(self) -> None:
        """Persist index and metadata to disk."""
        if self.index is not None:
            faiss.write_index(self.index, self.index_path)
            
            with open(self.meta_path, 'wb') as f:
                pickle.dump(self.metadata_store, f)
                
            logger.debug("Successfully saved FAISS index to disk", job_id=self.job_id)

    def load(self) -> bool:
        """Load index and metadata from disk. Returns True if successful."""
        if os.path.exists(self.index_path) and os.path.exists(self.meta_path):
            self.index = faiss.read_index(self.index_path)
            with open(self.meta_path, 'rb') as f:
                self.metadata_store = pickle.load(f)
            logger.debug("Successfully loaded FAISS index from disk", job_id=self.job_id)
            return True
        return False
        
    def search(self, query_embedding: np.ndarray, top_k: int = settings.TOP_K_CHUNKS) -> List[Tuple[ChunkMetadata, float]]:
        """
        Search for the top K most similar vectors.
        Returns a list of (metadata, distance) tuples.
        """
        if self.index is None or self.index.ntotal == 0:
            logger.warning("Searching an empty or uninitialized FAISS index", job_id=self.job_id)
            return []
            
        query_embedding = query_embedding.astype(np.float32)
        if len(query_embedding.shape) == 1:
            query_embedding = np.expand_dims(query_embedding, axis=0)
            
        # D is distances array, I is index array
        distances, indices = self.index.search(query_embedding, top_k)
        
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx != -1 and idx < len(self.metadata_store):
                results.append((self.metadata_store[idx], float(dist)))
                
        return results

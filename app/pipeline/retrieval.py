import json
from pathlib import Path
from typing import List

from app.core.logging import logger
from app.models.domain_models import ComplianceRule, ChunkMetadata
from app.pipeline.vector_store import FAISSVectorStore
from app.pipeline.embeddings import EmbeddingsGenerator

class DocumentRetriever:
    """Handles semantic extraction and deterministic risk filtering."""
    
    def __init__(self, embeddings_gen: EmbeddingsGenerator, vector_store: FAISSVectorStore):
        self.embeddings_gen = embeddings_gen
        self.vector_store = vector_store
        
    def _deterministic_filter(self, chunks: List[ChunkMetadata], rule: ComplianceRule) -> List[ChunkMetadata]:
        """
        Filter chunks using keyword-based risk scanning.
        """
        if not rule.keywords:
            return chunks

        filtered = []
        for chunk in chunks:
            chunk_lower = chunk.text.lower()
            # If any keyword matches the chunk text
            if any(kw.lower() in chunk_lower for kw in rule.keywords):
                filtered.append(chunk)

        pct = (len(filtered) / len(chunks)) * 100 if chunks else 0
        logger.debug(f"Deterministic filter retained {len(filtered)}/{len(chunks)} chunks ({pct:.1f}%) for rule {rule.rule_id}")
        return filtered

    def retrieve_relevant_chunks(self, rule: ComplianceRule) -> List[ChunkMetadata]:
        """
        Orchestration pattern:
        1. Embed the rule query
        2. Perform Semantic Vector Search to get top K
        3. Apply deterministic filter to ensure only high-risk chunks are evaluated
        """
        # Formulate query based on rule description or name
        query_text = rule.description or rule.rule or " ".join(rule.keywords)
        if not query_text:
            logger.warning(f"Rule {rule.rule_id} has no searchable text. Returning empty.")
            return []
            
        query_embedding = self.embeddings_gen.generate([query_text])[0]
        
        # Semantic Search in Vector DB
        search_results = self.vector_store.search(query_embedding)
        
        # Extract just the metadata objects
        candidate_chunks = [meta for meta, score in search_results]
        
        # Apply deterministic rule-based filtering
        filtered_chunks = self._deterministic_filter(candidate_chunks, rule)
        
        # If the deterministic filter is too strict and filters everything, 
        # fallback to the top vector matches to avoid false negatives.
        if not filtered_chunks and candidate_chunks:
             logger.debug(f"Fallback to semantic candidates for rule {rule.rule_id} as deterministic filter returned 0 results.")
             filtered_chunks = candidate_chunks[:3] # Returns top 3
             
        # Token estimation logic
        max_context_tokens = 4000
        # Rough token proxy: words * 1.3
        estimated_tokens = sum(len(chunk.text.split()) * 1.3 for chunk in filtered_chunks)
        
        if estimated_tokens > max_context_tokens:
            logger.warning(f"Context too large ({estimated_tokens} tokens) for rule {rule.rule_id}. Dropping lowest similarity chunks.")
            # Drop chunks from the end (least similar) until we fit
            while estimated_tokens > max_context_tokens and len(filtered_chunks) > 1:
                dropped_chunk = filtered_chunks.pop()
                estimated_tokens -= (len(dropped_chunk.text.split()) * 1.3)

        return filtered_chunks

def load_rules(jurisdiction: str = None) -> List[ComplianceRule]:
    """Helper to load compliance rules from the rules/ or policies/ directories based on requested jurisdiction."""
    rules = []
    
    # Simple hardcoded fallback for demonstration, load security rules from policies folder
    rules_dir = Path("rules")
    policies_dir = Path("policies")
    
    paths_to_load = []
    
    if policies_dir.exists():
        for file in policies_dir.glob("*.json"):
            paths_to_load.append(file)
            
    if rules_dir.exists():
        for file in rules_dir.glob("*.json"):
            if jurisdiction and jurisdiction.lower() not in file.stem.lower():
                continue
            paths_to_load.append(file)
            
    for path in paths_to_load:
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    for item in data:
                        rules.append(ComplianceRule(**item))
        except Exception as e:
            logger.error(f"Failed to load rule file {path}: {e}")
            
    return rules

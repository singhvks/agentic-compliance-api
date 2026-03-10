from app.core.config import settings
from app.core.llm.base import BaseLLM
from app.core.llm.openai_client import OpenAIClient
from app.core.llm.ollama_client import OllamaClient
from app.core.logging import logger

def get_llm_client() -> BaseLLM:
    """Factory function to get the appropriate LLM client based on configuration."""
    provider = settings.MODEL_PROVIDER.lower()
    
    logger.info("Initializing LLM client", provider=provider, model=settings.MODEL_NAME)
    
    if provider == "openai":
        return OpenAIClient()
    elif provider == "ollama":
        return OllamaClient()
    else:
        raise ValueError(f"Unsupported MODEL_PROVIDER '{provider}'. Use 'openai' or 'ollama'.")

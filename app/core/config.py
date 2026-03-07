import logging
import sys
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # App Settings
    PROJECT_NAME: str = "Compliance Analysis API"
    API_V1_STR: str = "/api/v1"
    
    # LLM Provider Configuration
    MODEL_PROVIDER: str = "openai"  # 'openai' or 'ollama'
    MODEL_NAME: str = "gpt-4o-mini"
    
    # OpenAI Settings
    OPENAI_API_KEY: Optional[str] = None
    
    # Ollama Settings
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    
    # Text Processing Settings
    CHUNK_SIZE: int = 800
    CHUNK_OVERLAP: int = 150
    
    # Embedding Settings
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    
    # Storage Settings
    VECTOR_STORE_PATH: str = "./analysisOutput/vector_store"
    DOCUMENT_STORE_PATH: str = "./analysisOutput/documents"
    
    # Retrieval Settings
    TOP_K_CHUNKS: int = 10
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()

# Setup logging
def setup_logging():
    logger = logging.getLogger("compliance_api")
    logger.setLevel(logging.INFO)
    
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"
    )
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    if not logger.handlers:
        logger.addHandler(console_handler)
        
    return logger

log = setup_logging()

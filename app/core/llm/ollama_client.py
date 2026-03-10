import json
import requests
from typing import Optional, Dict, Any
from app.core.llm.base import BaseLLM
from app.core.config import settings
from app.core.logging import logger

class OllamaClient(BaseLLM):
    """Local Ollama implementation of the BaseLLM interface."""
    
    def __init__(self, model_name: str = settings.MODEL_NAME, base_url: str = settings.OLLAMA_BASE_URL):
        self.model_name = model_name
        self.base_url = base_url.rstrip("/")
        self.generate_url = f"{self.base_url}/api/chat"
        
    def _prepare_messages(self, prompt: str, system_prompt: Optional[str] = None) -> list:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        return messages
        
    def generate(self, prompt: str, system_prompt: Optional[str] = None, response_format: Optional[Dict[str, Any]] = None) -> str:
        messages = self._prepare_messages(prompt, system_prompt)
        
        payload = {
            "model": self.model_name,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": 0.1
            }
        }
        
        # Ollama supports a boolean format flag for JSON
        if response_format and response_format.get("type") == "json_object":
            payload["format"] = "json"
            
        logger.debug("Generating response from Ollama", model=self.model_name, url=self.generate_url)
        
        try:
            response = requests.post(self.generate_url, json=payload, timeout=120)
            response.raise_for_status()
            data = response.json()
            return data.get("message", {}).get("content", "")
        except requests.exceptions.RequestException as e:
            logger.error("Ollama API request failed", error=str(e), model=self.model_name)
            raise RuntimeError(f"Failed to communicate with Ollama: {e}")
            
    def generate_json(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        return self.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            response_format={"type": "json_object"}
        )

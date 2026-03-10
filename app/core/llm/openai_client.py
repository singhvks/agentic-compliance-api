import json
from typing import Optional, Dict, Any
from app.core.llm.base import BaseLLM
from app.core.config import settings
from app.core.logging import logger

try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

class OpenAIClient(BaseLLM):
    """OpenAI implementation of the BaseLLM interface."""
    
    def __init__(self, model_name: str = settings.MODEL_NAME):
        if not HAS_OPENAI:
            raise ImportError("openai package is not installed. Please install it to use OpenAIClient.")
        
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY must be set in the environment.")
            
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model_name = model_name
        
    def _prepare_messages(self, prompt: str, system_prompt: Optional[str] = None) -> list:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        return messages
        
    def generate(self, prompt: str, system_prompt: Optional[str] = None, response_format: Optional[Dict[str, Any]] = None) -> str:
        messages = self._prepare_messages(prompt, system_prompt)
        
        kwargs = {
            "model": self.model_name,
            "messages": messages,
            "temperature": 0.1,  # Low temperature for analytical tasks
        }
        
        if response_format:
            kwargs["response_format"] = response_format
            
        logger.debug("Generating response from OpenAI", model=self.model_name)
        response = self.client.chat.completions.create(**kwargs)
        
        return response.choices[0].message.content or ""
        
    def generate_json(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        # OpenAI supports a specific JSON mode parameter
        return self.generate(
            prompt=prompt, 
            system_prompt=system_prompt,
            response_format={"type": "json_object"}
        )

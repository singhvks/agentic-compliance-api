from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List

class BaseLLM(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    def generate(self, prompt: str, system_prompt: Optional[str] = None, response_format: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate a response from the LLM.
        
        Args:
            prompt: The user prompt to send to the model.
            system_prompt: Optional system instructions.
            response_format: Optional dict specifying expected JSON schema or format requirements.
            
        Returns:
            The generated string response.
        """
        pass
    
    @abstractmethod
    def generate_json(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Generate a strictly JSON-formatted response from the LLM.
        
        Args:
            prompt: The user prompt.
            system_prompt: Optional system instructions.
            
        Returns:
            A string containing parsable JSON.
        """
        pass

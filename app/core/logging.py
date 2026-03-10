import sys
import logging
from typing import Any, Dict

class StructuredLogger:
    """A wrapper to provide structured logging metadata for the compliance API."""
    
    def __init__(self, name: str = "compliance_api"):
        self.logger = logging.getLogger(name)
        
    def info(self, msg: str, **kwargs: Any) -> None:
        self.logger.info(self._format_msg(msg, kwargs))
        
    def error(self, msg: str, **kwargs: Any) -> None:
        self.logger.error(self._format_msg(msg, kwargs))
        
    def warning(self, msg: str, **kwargs: Any) -> None:
        self.logger.warning(self._format_msg(msg, kwargs))
        
    def debug(self, msg: str, **kwargs: Any) -> None:
        self.logger.debug(self._format_msg(msg, kwargs))
        
    def _format_msg(self, msg: str, kwargs: Dict[str, Any]) -> str:
        if not kwargs:
            return msg
        metadata = ", ".join(f"{k}={v}" for k, v in kwargs.items())
        return f"{msg} | {metadata}"

logger = StructuredLogger()

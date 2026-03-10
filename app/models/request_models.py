from pydantic import BaseModel, ConfigDict
from typing import Optional

class AnalysisRequest(BaseModel):
    """
    Model for holding the parameters after parsing a multipart/form-data upload.
    Note: FastAPI route will extract these from Form() directly.
    """
    country: str
    industry: Optional[str] = None
    
    model_config = ConfigDict(extra="ignore")

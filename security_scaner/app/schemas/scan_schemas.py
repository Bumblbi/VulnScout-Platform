from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from app.models.scan_models import ScanType

class ScanRequest(BaseModel):
    target: str
    scan_type: ScanType
    options: Optional[Dict[str, Any]] = None

class ScanResponse(BaseModel):
    id: int
    target: str
    scan_type: str
    status: str
    start_time: datetime

    class Config:
        from_attributes = True
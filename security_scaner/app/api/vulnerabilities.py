from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.schemas.vulnerability_schemas import VulnerabilityResponse
from app.models.vulnerability_models import Vulnerability

router = APIRouter()

@router.get("/", response_model=List[VulnerabilityResponse])
async def get_vulnerabilities(
    severity: Optional[str] = None, 
    db: Session = Depends(get_db)
):
    query = db.query(Vulnerability)
    if severity:
        query = query.filter(Vulnerability.severity == severity)
    
    vulnerabilities = query.all()
    return vulnerabilities
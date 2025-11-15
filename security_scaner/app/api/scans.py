from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.scan_schemas import ScanRequest, ScanResponse
from app.models.scan_models import Scan, ScanStatus
from app.celery_app.tasks import scan_task

router = APIRouter()

@router.post("/", response_model=ScanResponse)
async def start_scan(
    scan_request: ScanRequest, 
    background_tasks: BackgroundTasks, 
    db: Session = Depends(get_db)
):
    scan = Scan(
        target=scan_request.target,
        scan_type=scan_request.scan_type,
        status=ScanStatus.PENDING,
        options=scan_request.options or {}
    )
    db.add(scan)
    db.commit()
    db.refresh(scan)
    
    task = scan_task.delay(scan.id)
    scan.celery_task_id = task.id
    db.commit()
    
    return scan

@router.get("/{scan_id}")
async def get_scan_status(scan_id: int, db: Session = Depends(get_db)):
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    return scan
from sqlalchemy import Column, String, Integer, DateTime, JSON, Enum, ForeignKey
from sqlalchemy.sql import func
from app.database import Base
import enum

class ScanType(enum.Enum):
    NETWORK = "network"
    WEB = "web"
    FULL = "full"
    CUSTOM = "custom"

class ScanStatus(enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    STOPPED = "stopped"

class Scan(Base):
    __tablename__ = 'scans'
    
    id = Column(Integer, primary_key=True)
    target = Column(String(255), nullable=False)
    scan_type = Column(Enum(ScanType), nullable=False)
    status = Column(Enum(ScanStatus), default=ScanStatus.PENDING)
    start_time = Column(DateTime, default=func.now())
    end_time = Column(DateTime)
    user_id = Column(Integer)
    options = Column(JSON)
    celery_task_id = Column(String(255))
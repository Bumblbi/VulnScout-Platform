from app.models.scan_models import Scan, ScanType, ScanStatus
from app.models.vulnerability_models import Host, Port, Vulnerability, SeverityLevel
from app.models.attack_models import AttackVector

# Импортируйте все модели, чтобы сделать их доступными для SQLAlchemy
__all__ = [
    'Scan', 'ScanType', 'ScanStatus',
    'Host', 'Port', 'Vulnerability', 'SeverityLevel',
    'AttackVector'
]

def create_tables():
    """Create all database tables"""
    from app.database import Base, engine
    Base.metadata.create_all(bind=engine)
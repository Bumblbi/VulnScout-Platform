from .celery_worker import celery_app
from app.database import SessionLocal
from app.models.scan_models import Scan, ScanStatus
from app.scanners.network_scanner import NetworkScanner
from app.scanners.vulnerability_scanner import VulnerabilityScanner
from app.utils.database_utils import save_scan_results

@celery_app.task(bind=True)
def scan_task(self, scan_id: int):
    db = SessionLocal()
    
    try:
        scan = db.query(Scan).filter(Scan.id == scan_id).first()
        if not scan:
            return
        
        scan.status = ScanStatus.RUNNING
        db.commit()
        
        # Запуск сканирования
        network_scanner = NetworkScanner()
        vuln_scanner = VulnerabilityScanner()
        
        network_data = network_scanner.scan_target(scan.target)
        vulnerabilities = vuln_scanner.scan(network_data)
        
        # Сохранение результатов
        save_scan_results(db, scan, network_data, vulnerabilities)
        
        scan.status = ScanStatus.COMPLETED
        db.commit()
        
    except Exception as e:
        scan.status = ScanStatus.FAILED
        db.commit()
        raise e
    finally:
        db.close()
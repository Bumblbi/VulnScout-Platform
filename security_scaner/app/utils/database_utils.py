from sqlalchemy.orm import Session
from typing import Dict, List, Optional
from app.models.scan_models import Scan, ScanStatus
from app.models.vulnerability_models import Vulnerability, SeverityLevel, Host, Port
from app.models.attack_models import AttackVector

def save_scan_results(db: Session, scan: Scan, network_data: Dict, vulnerabilities: List[Dict], attack_vectors: List[Dict] = None):
    """Сохранение результатов сканирования в БД"""
    
    # Сохранение хостов и портов
    host_map = {}
    for host_data in network_data.get('hosts', []):
        host = Host(
            scan_id=scan.id,
            ip_address=host_data['ip'],
            hostname=host_data.get('hostname'),
            os_info=host_data.get('os'),
            status=host_data.get('status', 'up')
        )
        db.add(host)
        db.flush()
        host_map[host_data['ip']] = host.id
        
        # Сохранение портов
        for port_data in host_data.get('ports', []):
            port = Port(
                host_id=host.id,
                port_number=port_data['port'],
                protocol=port_data.get('protocol', 'tcp'),
                service=port_data.get('service', 'unknown'),
                version=port_data.get('version', 'unknown'),
                state=port_data.get('state', 'open')
            )
            db.add(port)
            db.flush()

    # Сохранение уязвимостей
    for vuln_data in vulnerabilities:
        host_id = host_map.get(vuln_data['host'])
        port_id = find_port_id(db, vuln_data['host'], vuln_data['port']) if 'port' in vuln_data else None
        
        vulnerability = Vulnerability(
            scan_id=scan.id,
            host_id=host_id,
            port_id=port_id,
            title=vuln_data['vulnerability'].get('cve', {}).get('id', 'Unknown vulnerability'),
            description=vuln_data['vulnerability'].get('descriptions', [{}])[0].get('value', 'No description'),
            severity=map_severity(vuln_data['vulnerability'].get('metrics', {})),
            cvss_score=get_cvss_score(vuln_data['vulnerability']),
            cve_id=vuln_data['vulnerability'].get('cve', {}).get('id'),
            recommendation=generate_recommendation(vuln_data['vulnerability']),
            module_source='vulnerability_scanner'
        )
        db.add(vulnerability)

    # Сохранение векторов атак
    if attack_vectors:
        for vector in attack_vectors:
            attack_vector = AttackVector(
                scan_id=scan.id,
                description=vector['description'],
                confidence=vector.get('confidence', 0.5)
            )
            db.add(attack_vector)

    db.commit()

def find_port_id(db: Session, host_ip: str, port_number: int) -> Optional[int]:
    """Поиск ID порта по IP и номеру порта"""
    port = db.query(Port).join(Host).filter(
        Host.ip_address == host_ip,
        Port.port_number == port_number
    ).first()
    return port.id if port else None

def find_host_id(db: Session, scan_id: int, host_ip: str) -> Optional[int]:
    """Поиск ID хоста по IP и scan_id"""
    host = db.query(Host).filter(
        Host.scan_id == scan_id,
        Host.ip_address == host_ip
    ).first()
    return host.id if host else None

def map_severity(metrics: Dict) -> SeverityLevel:
    """Маппинг severity из CVSS в наш enum"""
    cvss_v3 = metrics.get('cvssMetricV3', [{}])[0].get('cvssData', {})
    base_score = cvss_v3.get('baseScore', 0)
    
    if base_score >= 9.0:
        return SeverityLevel.CRITICAL
    elif base_score >= 7.0:
        return SeverityLevel.HIGH
    elif base_score >= 4.0:
        return SeverityLevel.MEDIUM
    elif base_score >= 0.1:
        return SeverityLevel.LOW
    else:
        return SeverityLevel.INFO

def get_cvss_score(vulnerability: Dict) -> float:
    """Извлечение CVSS score из данных уязвимости"""
    metrics = vulnerability.get('metrics', {})
    cvss_v3 = metrics.get('cvssMetricV3', [{}])[0].get('cvssData', {})
    return cvss_v3.get('baseScore', 0.0)

def generate_recommendation(vulnerability: Dict) -> str:
    """Генерация рекомендации по исправлению"""
    cve_id = vulnerability.get('cve', {}).get('id', 'Unknown')
    return f"Apply security patches for {cve_id}. Update affected software to latest version."

def cleanup_old_scans(db: Session, days_old: int = 30):
    """Очистка старых сканирований"""
    from datetime import datetime, timedelta
    from sqlalchemy import and_
    
    cutoff_date = datetime.now() - timedelta(days=days_old)
    
    # Находим старые сканирования
    old_scans = db.query(Scan).filter(
        and_(
            Scan.status.in_([ScanStatus.COMPLETED, ScanStatus.FAILED]),
            Scan.start_time < cutoff_date
        )
    ).all()
    
    for scan in old_scans:
        # Удаляем связанные данные (каскадное удаление должно быть настроено в моделях)
        db.delete(scan)
    
    db.commit()
    return len(old_scans)
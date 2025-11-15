from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
import json
import os
from datetime import datetime

from app.database import get_db
from app.models.scan_models import Scan, ScanStatus
from app.models.vulnerability_models import Vulnerability, SeverityLevel, Host, Port
from app.models.attack_models import AttackVector
from app.utils.report_generator import generate_pdf_report, generate_html_report

router = APIRouter()

@router.get("/{scan_id}")
async def get_report(
    scan_id: int, 
    format: str = "json",
    db: Session = Depends(get_db)
):
    """Генерация отчета по сканированию в различных форматах"""
    
    # Получаем данные сканирования
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    if scan.status != ScanStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Scan is not completed yet")
    
    # Собираем данные для отчета
    report_data = generate_report_data(scan, db)
    
    # Генерируем отчет в нужном формате
    if format == "json":
        return report_data
    
    elif format == "pdf":
        pdf_path = generate_pdf_report(report_data, scan_id)
        return FileResponse(
            pdf_path, 
            media_type='application/pdf',
            filename=f"security_report_scan_{scan_id}.pdf"
        )
    
    elif format == "html":
        html_path = generate_html_report(report_data, scan_id)
        return FileResponse(
            html_path,
            media_type='text/html',
            filename=f"security_report_scan_{scan_id}.html"
        )
    
    else:
        raise HTTPException(status_code=400, detail="Unsupported format. Use: json, pdf, html")

@router.get("/{scan_id}/summary")
async def get_report_summary(scan_id: int, db: Session = Depends(get_db)):
    """Краткая сводка по сканированию"""
    
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    # Статистика по уязвимостям
    vuln_stats = db.query(
        Vulnerability.severity,
        db.func.count(Vulnerability.id)
    ).filter(
        Vulnerability.scan_id == scan_id
    ).group_by(Vulnerability.severity).all()
    
    # Количество хостов и портов
    hosts_count = db.query(Host).filter(Host.scan_id == scan_id).count()
    ports_count = db.query(Port).filter(Port.host_id.in_(
        db.query(Host.id).filter(Host.scan_id == scan_id)
    )).count()
    
    return {
        "scan_id": scan_id,
        "target": scan.target,
        "status": scan.status.value,
        "start_time": scan.start_time.isoformat() if scan.start_time else None,
        "end_time": scan.end_time.isoformat() if scan.end_time else None,
        "duration": str(scan.end_time - scan.start_time) if scan.end_time and scan.start_time else None,
        "summary": {
            "hosts_scanned": hosts_count,
            "ports_found": ports_count,
            "vulnerabilities_found": sum(count for _, count in vuln_stats),
            "vulnerabilities_by_severity": {
                severity.value: count for severity, count in vuln_stats
            }
        }
    }

@router.get("/{scan_id}/vulnerabilities")
async def get_scan_vulnerabilities(
    scan_id: int,
    severity: str = None,
    db: Session = Depends(get_db)
):
    """Получить все уязвимости конкретного сканирования"""
    
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    query = db.query(Vulnerability).filter(Vulnerability.scan_id == scan_id)
    
    if severity:
        try:
            severity_enum = SeverityLevel(severity)
            query = query.filter(Vulnerability.severity == severity_enum)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid severity level")
    
    vulnerabilities = query.all()
    
    return {
        "scan_id": scan_id,
        "vulnerabilities": [
            {
                "id": vuln.id,
                "title": vuln.title,
                "severity": vuln.severity.value,
                "cvss_score": vuln.cvss_score,
                "host": vuln.host.ip_address if vuln.host else "N/A",
                "port": vuln.port.port_number if vuln.port else None,
                "service": vuln.port.service if vuln.port else "N/A",
                "description": vuln.description,
                "recommendation": vuln.recommendation
            }
            for vuln in vulnerabilities
        ]
    }

@router.get("/{scan_id}/attack-vectors")
async def get_attack_vectors(scan_id: int, db: Session = Depends(get_db)):
    """Получить цепочки атак для сканирования"""
    
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    attack_vectors = db.query(AttackVector).filter(AttackVector.scan_id == scan_id).all()
    
    return {
        "scan_id": scan_id,
        "attack_vectors": [
            {
                "id": av.id,
                "source": av.source_vulnerability.title if av.source_vulnerability else "Initial Access",
                "target": av.target_vulnerability.title if av.target_vulnerability else "Final Objective",
                "description": av.description,
                "confidence": av.confidence
            }
            for av in attack_vectors
        ]
    }

def generate_report_data(scan: Scan, db: Session) -> dict:
    """Генерация данных для отчета"""
    
    # Получаем все связанные данные
    hosts = db.query(Host).filter(Host.scan_id == scan.id).all()
    vulnerabilities = db.query(Vulnerability).filter(Vulnerability.scan_id == scan.id).all()
    attack_vectors = db.query(AttackVector).filter(AttackVector.scan_id == scan.id).all()
    
    # Статистика по уязвимостям
    vuln_by_severity = {}
    for severity in SeverityLevel:
        count = db.query(Vulnerability).filter(
            Vulnerability.scan_id == scan.id,
            Vulnerability.severity == severity
        ).count()
        vuln_by_severity[severity.value] = count
    
    # Топ критических уязвимостей
    critical_vulns = [
        {
            "title": vuln.title,
            "cvss_score": vuln.cvss_score,
            "host": vuln.host.ip_address if vuln.host else "N/A",
            "port": vuln.port.port_number if vuln.port else None
        }
        for vuln in vulnerabilities 
        if vuln.severity == SeverityLevel.CRITICAL
    ][:10]  # Ограничиваем 10 самыми критическими
    
    report_data = {
        "report_metadata": {
            "scan_id": scan.id,
            "target": scan.target,
            "scan_type": scan.scan_type.value,
            "generated_at": datetime.now().isoformat(),
            "scan_start_time": scan.start_time.isoformat() if scan.start_time else None,
            "scan_end_time": scan.end_time.isoformat() if scan.end_time else None
        },
        "executive_summary": {
            "total_hosts_scanned": len(hosts),
            "total_vulnerabilities_found": len(vulnerabilities),
            "vulnerability_distribution": vuln_by_severity,
            "overall_risk_score": calculate_risk_score(vulnerabilities),
            "top_critical_vulnerabilities": critical_vulns
        },
        "detailed_findings": {
            "hosts": [
                {
                    "ip_address": host.ip_address,
                    "hostname": host.hostname,
                    "os_info": host.os_info,
                    "open_ports": [
                        {
                            "port": port.port_number,
                            "service": port.service,
                            "version": port.version
                        }
                        for port in host.ports
                        if port.state == 'open'
                    ]
                }
                for host in hosts
            ],
            "vulnerabilities": [
                {
                    "id": vuln.id,
                    "title": vuln.title,
                    "severity": vuln.severity.value,
                    "cvss_score": vuln.cvss_score,
                    "host": vuln.host.ip_address if vuln.host else "N/A",
                    "port": vuln.port.port_number if vuln.port else None,
                    "description": vuln.description,
                    "recommendation": vuln.recommendation,
                    "cve_id": vuln.cve_id,
                    "proof": vuln.proof
                }
                for vuln in vulnerabilities
            ]
        },
        "attack_analysis": {
            "attack_vectors": [
                {
                    "source": av.source_vulnerability.title if av.source_vulnerability else "External",
                    "target": av.target_vulnerability.title if av.target_vulnerability else "Target System",
                    "description": av.description,
                    "confidence": av.confidence
                }
                for av in attack_vectors
            ]
        },
        "recommendations": generate_recommendations(vulnerabilities)
    }
    
    return report_data

def calculate_risk_score(vulnerabilities: List[Vulnerability]) -> float:
    """Расчет общего уровня риска"""
    if not vulnerabilities:
        return 0.0
    
    severity_weights = {
        SeverityLevel.CRITICAL: 10.0,
        SeverityLevel.HIGH: 7.5,
        SeverityLevel.MEDIUM: 5.0,
        SeverityLevel.LOW: 2.5,
        SeverityLevel.INFO: 1.0
    }
    
    total_score = sum(
        severity_weights[vuln.severity] * (vuln.cvss_score or 1.0)
        for vuln in vulnerabilities
    )
    
    return min(total_score / len(vulnerabilities), 10.0)

def generate_recommendations(vulnerabilities: List[Vulnerability]) -> List[dict]:
    """Генерация рекомендаций по исправлению"""
    recommendations = []
    
    # Группируем рекомендации по типам уязвимостей
    vuln_by_type = {}
    for vuln in vulnerabilities:
        if vuln.title not in vuln_by_type:
            vuln_by_type[vuln.title] = []
        vuln_by_type[vuln.title].append(vuln)
    
    for vuln_type, vuln_list in vuln_by_type.items():
        critical_count = len([v for v in vuln_list if v.severity in [SeverityLevel.CRITICAL, SeverityLevel.HIGH]])
        
        recommendations.append({
            "vulnerability_type": vuln_type,
            "affected_systems": len(set(v.host.ip_address for v in vuln_list if v.host)),
            "critical_instances": critical_count,
            "recommendation": vuln_list[0].recommendation if vuln_list[0].recommendation else "Apply security patches and updates",
            "priority": "HIGH" if critical_count > 0 else "MEDIUM"
        })
    
    return sorted(recommendations, key=lambda x: x["priority"], reverse=True)
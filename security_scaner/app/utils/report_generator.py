import os
import json
from datetime import datetime
from typing import Dict
from playwright.sync_api import sync_playwright  # ⬅️ Только это нужно
import tempfile

# Настройка директории для отчётов
REPORTS_DIR = "reports"
os.makedirs(REPORTS_DIR, exist_ok=True)


def generate_pdf_report(report_data: Dict, scan_id: int) -> str:
    """
    Генерирует PDF-отчёт из HTML с использованием Playwright (Chromium)
    """
    html_content = generate_html_content(report_data, scan_id)

    filename = f"scan_{scan_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf_path = os.path.join(REPORTS_DIR, filename)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_content(html_content, wait_until="networkidle")
        page.pdf(
            path=pdf_path,
            format="A4",
            margin={"top": "10mm", "bottom": "10mm", "left": "10mm", "right": "10mm"},
            print_background=True
        )
        browser.close()

    return pdf_path


def generate_html_report(report_data: Dict, scan_id: int) -> str:
    html_content = generate_html_content(report_data, scan_id)
    html_dir = os.path.join(REPORTS_DIR, "html")
    os.makedirs(html_dir, exist_ok=True)
    filename = f"scan_{scan_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    filepath = os.path.join(html_dir, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html_content)
    return filepath


def generate_html_content(report_data: Dict, scan_id: int) -> str:
    exec_summary = report_data['executive_summary']
    detailed_findings = report_data['detailed_findings']

    vuln_dist_rows = "".join(
        f"<tr><td class='{sev}'>{sev.title()}</td><td>{count}</td></tr>"
        for sev, count in exec_summary['vulnerability_distribution'].items()
    )

    critical_vulns_rows = "".join(
        f"<tr><td>{vuln['title']}</td><td>{vuln.get('cvss_score', 'N/A')}</td><td>{vuln['host']}</td><td>{vuln.get('port', 'N/A')}</td></tr>"
        for vuln in exec_summary.get('top_critical_vulnerabilities', [])
    )

    host_sections = "".join(
        f"<h4>{host['ip_address']} ({host.get('hostname', 'N/A')})</h4><ul>{''.join(f'<li><strong>Port {port['port']}:</strong> {port['service']} {port.get('version', '')}</li>' for port in host.get('open_ports', []))}</ul>"
        for host in detailed_findings.get('hosts', [])
    )

    vulns_rows = "".join(
        f"<tr><td>{vuln['title']}</td><td class='{vuln['severity']}'>{vuln['severity'].title()}</td><td>{vuln.get('cvss_score', 'N/A')}</td><td>{vuln['host']}:{vuln.get('port', 'N/A')}</td></tr>"
        for vuln in detailed_findings.get('vulnerabilities', [])
    )

    recommendations = "".join(
        f"<li><strong>{rec['vulnerability_type']}</strong> (Priority: {rec['priority']}): {rec['recommendation']}</li>"
        for rec in report_data.get('recommendations', [])
    )

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Security Report - Scan #{scan_id}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            .header {{ background: #2c3e50; color: white; padding: 20px; border-radius: 5px; }}
            .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
            .critical {{ color: #e74c3c; font-weight: bold; }}
            .high {{ color: #e67e22; }}
            .medium {{ color: #f39c12; }}
            .low {{ color: #3498db; }}
            .info {{ color: #27ae60; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background-color: #f2f2f2; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>VulnScout Security Assessment Report</h1>
            <p>Scan ID: {scan_id} | Target: {report_data['report_metadata']['target']} | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
        </div>
        <div class="section">
            <h2>Executive Summary</h2>
            <p><strong>Total Hosts Scanned:</strong> {exec_summary['total_hosts_scanned']}</p>
            <p><strong>Total Vulnerabilities Found:</strong> {exec_summary['total_vulnerabilities_found']}</p>
            <p><strong>Overall Risk Score:</strong> {exec_summary['overall_risk_score']:.1f}/10.0</p>
            <h3>Vulnerability Distribution</h3>
            <table><tr><th>Severity</th><th>Count</th></tr>{vuln_dist_rows}</table>
        </div>
        <div class="section">
            <h2>Top Critical Vulnerabilities</h2>
            <table><tr><th>Vulnerability</th><th>CVSS Score</th><th>Host</th><th>Port</th></tr>{critical_vulns_rows}</table>
        </div>
        <div class="section">
            <h2>Detailed Findings</h2>
            <h3>Hosts</h3>{host_sections}
            <h3>Vulnerabilities</h3>
            <table><tr><th>Title</th><th>Severity</th><th>CVSS</th><th>Host:Port</th></tr>{vulns_rows}</table>
        </div>
        <div class="section">
            <h2>Recommendations</h2>
            <ol>{recommendations}</ol>
        </div>
        <div class="section">
            <p><em>Report generated by VulnScout Platform</em></p>
        </div>
    </body>
    </html>
    """


def save_json_report(report_data: Dict, scan_id: int) -> str:
    os.makedirs(REPORTS_DIR, exist_ok=True)
    filename = f"scan_{scan_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    filepath = os.path.join(REPORTS_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)
    return filepath

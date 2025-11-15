from app.utils.database_utils import (
    save_scan_results,
    find_port_id,
    find_host_id,
    map_severity,
    get_cvss_score,
    generate_recommendation,
    cleanup_old_scans
)

from app.utils.report_generator import (
    generate_pdf_report,
    generate_html_report,
    generate_html_content,
    save_json_report
)

__all__ = [
    'save_scan_results',
    'find_port_id', 
    'find_host_id',
    'map_severity',
    'get_cvss_score',
    'generate_recommendation',
    'cleanup_old_scans',
    'generate_pdf_report',
    'generate_html_report',
    'generate_html_content',
    'save_json_report'
]
from app.api.scans import router as scans_router
from app.api.vulnerabilities import router as vulnerabilities_router
from app.api.reports import router as reports_router

__all__ = [
    'scans_router',
    'vulnerabilities_router', 
    'reports_router'
]

# API version
API_VERSION = "v1"
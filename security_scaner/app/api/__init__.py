from .scans import router as scans_router
from .vulnerabilities import router as vulnerabilities_router
from .reports import router as reports_router

__all__ = ['scans_router', 'vulnerabilities_router', 'reports_router']
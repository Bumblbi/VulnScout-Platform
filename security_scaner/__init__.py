__version__ = "1.0.0"
__author__ = "VulnScout Team"

# Импорт пакетов для облегчения доступа
from app.main import app
from app.database import init_db, get_db
from app.models import create_tables

__all__ = [
    'app',
    'init_db',
    'get_db', 
    'create_tables'
]
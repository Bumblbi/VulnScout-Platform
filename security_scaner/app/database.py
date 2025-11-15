from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config.settings import settings

# Создаем движок с настройками пула соединений
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Проверка соединения перед использованием
    pool_recycle=3600,   # Переподключение каждый час
    echo=False  # Логирование SQL запросов (True для отладки)
)

# Фабрика сессий
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Базовый класс для моделей
Base = declarative_base()

# Dependency для FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Функция для создания таблиц
def init_db():
    """Создает все таблицы в базе данных"""
    from app.models.scan_models import Scan, Host, Port
    from app.models.vulnerability_models import Vulnerability
    from app.models.attack_models import AttackVector
    
    Base.metadata.create_all(bind=engine)
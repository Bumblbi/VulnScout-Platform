import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "mysql+pymysql://user:password@localhost/security_scanner"
    
    # Redis for Celery
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # API Settings
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = "your-secret-key"
    
    # External APIs
    CVE_API_URL: str = "https://services.nvd.nist.gov/rest/json/cves/2.0"
    FSTEK_API_URL: str = "https://bdu.fstec.ru/api/vulnerabilities"

settings = Settings()
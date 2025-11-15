from app.api import scans_router, vulnerabilities_router, reports_router
from fastapi import FastAPI
from app.api import scans_router, vulnerabilities_router
from app.database import engine, Base
from config.settings import settings

# Создание таблиц
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Security Assessment Tool")

# Подключение роутеров
app.include_router(scans_router, prefix="/api/v1/scans", tags=["scans"])
app.include_router(vulnerabilities_router, prefix="/api/v1/vulnerabilities", tags=["vulnerabilities"])

@app.get("/")
async def root():
    return {"message": "Security Assessment Tool API"}

# Подключение роутеров
app.include_router(scans_router, prefix="/api/v1/scans", tags=["scans"])
app.include_router(vulnerabilities_router, prefix="/api/v1/vulnerabilities", tags=["vulnerabilities"])
app.include_router(reports_router, prefix="/api/v1/reports", tags=["reports"])
from app.celery_app.celery_worker import celery_app
from app.celery_app.tasks import scan_task

__all__ = [
    'celery_app',
    'scan_task'
]
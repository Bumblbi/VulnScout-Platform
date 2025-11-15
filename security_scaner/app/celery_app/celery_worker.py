from celery import Celery
from config.settings import settings

celery_app = Celery('security_scanner')
celery_app.conf.broker_url = settings.REDIS_URL
celery_app.conf.result_backend = settings.REDIS_URL

# Автоматическое обнаружение задач
celery_app.autodiscover_tasks(['app.celery_app.tasks'])
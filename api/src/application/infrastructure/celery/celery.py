import os

from celery import Celery


"""
Celery app singleton. Mostly used to decorate tasks.
"""
celery_app = Celery('VCF Handler API')
celery_app.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379")
celery_app.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379")


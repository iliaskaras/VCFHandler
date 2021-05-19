from celery import Celery
from flask import Flask


def init_celery(celery: Celery, app: Flask):
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTast(TaskBase):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTast

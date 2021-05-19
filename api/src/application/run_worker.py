from application.factories import vcf_handler_api
from application.infrastructure.celery.celery import celery_app
from application.infrastructure.celery.celery_utils import init_celery

application = vcf_handler_api(
    name="VCF Handler API"
)

celery = init_celery(
        celery=celery_app,
        app=application
    )

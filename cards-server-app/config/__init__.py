from config.celery import app as celery_app
from django.conf import settings

if settings.TESTING:
    print("TESTING is active: Will not start Celery")
else:
    __all__ = ("celery_app",)

from .base import *

ALLOWED_HOSTS = ["localhost", "testserver"]

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "TEST_DJANGO_SECRET_KEY"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TESTING = True

CELERY_ALWAYS_EAGER = True  # so celery does not error
CELERY_BROKER_URL = "redis://localhost:6379"
CELERY_RESULT_BACKEND = "redis://localhost:6379"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "circle_test",
        "USER": "ubuntu",
        "PASSWORD": "test",
        "HOST": "localhost",
        "PORT": "5432",
    }
}

AWS_STORAGE_BUCKET_NAME = "NOT_SET_AWS_STORAGE_BUCKET_NAME"
AWS_S3_CUSTOM_DOMAIN = "%s.s3.amazonaws.com" % AWS_STORAGE_BUCKET_NAME

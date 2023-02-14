import logging
from .base import *

logger = logging.getLogger("setting_warnings")

# LOGGING
LOGGING = {
    "version": 1,
    "loggers": {
        "setting_warnings": {
            "level": "WARNING"
        },
    }
}

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

ALLOWED_HOSTS = [""]  # TODO: Set ALLOWED_HOSTS
CORS_ALLOWED_ORIGINS = [""]  # TODO: Set CORS_ALLOWED_ORIGINS or CORS_ALLOWED_ORIGIN_REGEXES

if all([host in ["", "*"] for host in ALLOWED_HOSTS]):
    logger.warning('WARNING: The settings.ALLOWED_HOSTS should not be "" or "*" on production. ')

if all([origin in ["", "*"] for origin in CORS_ALLOWED_ORIGINS]):
    logger.warning('WARNING: The settings.CORS_ALLOWED_ORIGINS should not be "" or "*" on production. ')


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("RDS_DB_NAME"),
        "USER": os.environ.get("RDS_USERNAME"),
        "PASSWORD": os.environ.get("RDS_PASSWORD"),
        "HOST": os.environ.get("RDS_HOST"),
        "PORT": os.environ.get("RDS_PORT", "5432"),
    }
}

AWS_STORAGE_BUCKET_NAME = "cards-prod"
AWS_S3_CUSTOM_DOMAIN = "%s.s3.amazonaws.com" % AWS_STORAGE_BUCKET_NAME

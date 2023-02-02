from .base import *

DEBUG = True

SECRET_KEY = "django-insecure-pc&dqbfctn1@-rl3@s813bo(id*%rtl#zsg6trq(vp4^6@ae#!"

ALLOWED_HOSTS = ["*"]
CORS_ORIGIN_ALLOW_ALL = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "postgres",
        "USER": "postgres",
        "PASSWORD": "password",
        "HOST": "db",
        "PORT": "5432",
    }
}

AWS_STORAGE_BUCKET_NAME = "NOT_SET_AWS_STORAGE_BUCKET_NAME"
AWS_S3_CUSTOM_DOMAIN = "%s.s3.amazonaws.com" % AWS_STORAGE_BUCKET_NAME

if DEBUG:
    print("Dev Mode: Sending emails locally")
    EMAIL_HOST = "mailcatcher"
    EMAIL_HOST_USER = ""
    EMAIL_HOST_PASSWORD = ""
    EMAIL_PORT = 1025
    EMAIL_USE_TLS = False

SUPER_ADMIN_PASS = "cfb1234567q"

LOGGING = {
    "version": 1,
    "loggers": {
        "django.db.backends": {
            "level": "DEBUG"
        }
    }
}

# for django-debug-toolbar
if DEBUG:
    import socket  # only if you haven't already imported this

    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
    INTERNAL_IPS = [ip[: ip.rfind(".")] + ".1" for ip in ips] + ["127.0.0.1", "10.0.2.2"]


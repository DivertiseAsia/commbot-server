# Health Check Middleware
For request path `{base_url}/ht/`, This middleware would ignore the `ALLOWED_HOSTS` validation which Django's `django.middleware.common.CommonMiddleware` calls request.get_host(), 

## Why?
In some cases, the IP of health-checker is dynamic (i.e. AWS target group health check)

If you simply want to check that the application is running, this middleware is your another option

## Set Up
1. Add middleware into `MIDDLEWARE` config in `settings.py`
    ***NOTE:*** put the `HealthCheckMiddleware` above the `CommonMiddleware`
```python
MIDDLEWARE = [
    ...,
    "config.middleware.healthcheck.HealthCheckMiddleware",
    "django.middleware.common.CommonMiddleware",
    ...,
]
```

from django.http import HttpResponse


class HealthCheckMiddleware:
    """
    Health Check Middleware
    ---
    If request path is "/ht" or "/ht/" this middleware would ignore the `ALLOWED_HOSTS` validation which Django's
    `django.middleware.common.CommonMiddleware` calls request.get_host()
    
    Ensure that this middleware places above the `django.middleware.common.CommonMiddleware`
    """
    def __init__(self, get_response):
        # One-time configuration and initialization.
        self.get_response = get_response

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        if request.path in ["/ht", "/ht/"]:
            return HttpResponse("OK")

        return self.get_response(request)

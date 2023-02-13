from django.http import HttpResponse


class HealthCheckMiddleware:

    def __init__(self, get_response):
        # One-time configuration and initialization.
        self.get_response = get_response

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        if request.path in ["/ht", "/ht/"]:
            return HttpResponse("OK")

        return self.get_response(request)

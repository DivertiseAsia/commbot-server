from django.conf import settings as proj_settings
from django.urls import resolve
from django.urls.exceptions import Resolver404
from django.utils import timezone


class SlowAPIAlertMiddleware:

    def __init__(self, get_response):
        # One-time configuration and initialization.
        self.alert_at_ms = None
        self.alert_namespaces = None
        self.get_response = get_response

    def is_validate(self):
        self.alert_namespaces = getattr(proj_settings, "SLOW_API_ALERT_NAMESPACES", None)
        self.alert_at_ms = getattr(proj_settings, "SLOW_API_ALERT_AT_MS", None)

        if not self.alert_namespaces or not self.alert_at_ms:
            return False

        return True

    def is_api_alert_request(self, request):
        """
        Determine if the request namespace in settings.SLOW_API_ALERT_NAMESPACES.
        """
        try:
            # The primary caller of this function is in the middleware which may
            # not have resolver_match set.
            resolver_match = request.resolver_match or resolve(
                request.path, getattr(request, "urlconf", None)
            )
        except Resolver404:
            return False

        return resolver_match.namespaces and resolver_match.namespaces[-1] in self.alert_namespaces

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        print(f">>> MIDDLEWARE req: {request}")
        if not self.is_validate() or not self.is_api_alert_request(request):
            return self.get_response(request)

        req_time = timezone.now()
        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.
        print(f">>> MIDDLEWARE response: {response}")
        request_durations = timezone.now() - req_time
        if request_durations.total_seconds() * 1000 >= self.alert_at_ms:
            # TODO: Send email
            print("!! Alert!!")
        return response

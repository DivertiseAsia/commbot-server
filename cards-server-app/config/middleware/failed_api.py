from django.conf import settings
from django.dispatch import Signal
from django.urls import resolve
from django.urls.exceptions import Resolver404

"""
Signal arguments: 
    request: HttpRequest
    request_body: byte string
    response: HttpResponse
    alert_data: dict
"""
failed_api_alert_triggered = Signal()


class FailedAPIAlertMiddleware:

    def __init__(self, get_response):
        # One-time configuration and initialization.
        self.alert_namespaces = getattr(settings, "FAILED_API_ALERT_NAMESPACES", None)
        self.status_codes = getattr(settings, "FAILED_API_ALERT_STATUS_CODES", None)
        self.get_response = get_response

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

    def trigger_alert(self, request, request_body, response):
        """
        request_body parameter used for avoid error
        RawPostDataException: You cannot access body after reading from request's data stream
        """
        alert_data = {
            "request": {
                "method": request.method,
                "url": request.path,
                "body": request_body,
            },
            "response": {
                "status_code": response.status_code,
                "content": response.content
            },
            "sent_from": request.get_host()
        }

        # send a signal that api failed alert has triggered
        # let whoever receives this signal handle alert method
        failed_api_alert_triggered.send(
            sender=self.__class__, request=request, request_body=request_body, response=response, alert_data=alert_data
        )

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        if not self.is_api_alert_request(request):
            return self.get_response(request)

        # store request.body to avoid error
        # RawPostDataException: You cannot access body after reading from request's data stream
        request_body = request.body
        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.
        if response.status_code in self.status_codes:
            self.trigger_alert(request, request_body, response)

        return response

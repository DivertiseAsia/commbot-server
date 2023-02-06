from django.conf import settings
from django.core import mail
from django.template.loader import render_to_string
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
        self.alert_namespaces = getattr(settings, "SLOW_API_ALERT_NAMESPACES", None)
        self.alert_at_ms = getattr(settings, "SLOW_API_ALERT_AT_MS", None)

        if not self.alert_at_ms or not self.alert_namespaces:
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

    def send_mail_to_staff(self, request, response, request_duration_ms, request_at, response_at):
        from django.contrib.auth import get_user_model
        User = get_user_model()

        context = {
            "alert_at_ms": self.alert_at_ms,
            "request_duration_ms": request_duration_ms,
            "request": {
                "at": f"{request_at}",  # datetime with timezone
                "method": request.method,
                "url": request.path,
            },
            "response": {
                "at": f"{response_at}",
                "status_code": response.status_code,
            },
        }
        recipient_list = User.objects.filter(is_superuser=True).values_list("email", flat=True)

        mail.send_mail(
            subject="[Alert] Slow API detected",
            message=render_to_string("./email/slow_api_alert/slow_api_alert.txt", context),
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@divertise.asia"),
            recipient_list=recipient_list,
            html_message=render_to_string("./email/slow_api_alert/slow_api_alert.html", context),
            fail_silently=False,
        )

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        if not self.is_validate() or not self.is_api_alert_request(request):
            return self.get_response(request)

        req_time = timezone.now()
        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.
        resp_time = timezone.now()
        request_duration_ms = (resp_time - req_time).total_seconds() * 1000

        if request_duration_ms >= self.alert_at_ms:
            self.send_mail_to_staff(request, response, request_duration_ms, request_at=req_time, response_at=resp_time)

        return response

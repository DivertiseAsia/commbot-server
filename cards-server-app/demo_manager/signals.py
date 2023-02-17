import logging

from django.contrib.auth import get_user_model
from django.core import mail
from django.dispatch import receiver
from django.template.loader import render_to_string

from config.helpers import get_no_reply_email
from config.middleware.failed_api import failed_api_alert_triggered
from config.middleware.slow_api import slow_api_alert_triggered

User = get_user_model()

logger = logging.getLogger("root")


@receiver(slow_api_alert_triggered)
def handle_slow_api_alert_triggered(sender, alert_data, *args, **kwargs):
    logger.warning(f"WARNING: Slow API detected {alert_data['request']['method']} {alert_data['request']['url']} "
                   f"request at: {alert_data['request']['at']}, response at: {alert_data['response']['at']}")

    recipient_list = User.objects.filter(is_superuser=True).values_list("email", flat=True)

    mail.send_mail(
        subject="[Alert] Slow API detected",
        message=render_to_string("./email/slow_api_alert/slow_api_alert.txt", alert_data),
        from_email=get_no_reply_email(),
        recipient_list=recipient_list,
        html_message=render_to_string("./email/slow_api_alert/slow_api_alert.html", alert_data),
        fail_silently=False,
    )


@receiver(failed_api_alert_triggered)
def handle_failed_api_alert_triggered(sender, request, request_body, response, alert_data, *args, **kwargs):
    logger.warning(f"WARNING: Failed API detected {response.status_code} {request.method} {request.path} alert_data: {alert_data}")

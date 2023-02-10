from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import mail
from django.dispatch import receiver
from django.template.loader import render_to_string

from config.middleware.slow_api import slow_api_alert_triggered

User = get_user_model()


@receiver(slow_api_alert_triggered)
def handle_slow_api_alert_triggered(sender, alert_data):
    recipient_list = User.objects.filter(is_superuser=True).values_list("email", flat=True)

    mail.send_mail(
        subject="[Alert] Slow API detected",
        message=render_to_string("./email/slow_api_alert/slow_api_alert.txt", alert_data),
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@divertise.asia"),
        recipient_list=recipient_list,
        html_message=render_to_string("./email/slow_api_alert/slow_api_alert.html", alert_data),
        fail_silently=False,
    )

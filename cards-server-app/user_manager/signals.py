from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django_rest_passwordreset.signals import reset_password_token_created
from social_django.models import UserSocialAuth

from config.helpers import get_no_reply_email
from user_manager.models import Profile

FRONTEND_URL = getattr(settings, "FRONTEND_URL", "")
DEFAULT_FROM_EMAIL = get_no_reply_email()


@receiver(reset_password_token_created)
def password_reset_token_created(
    sender, instance, reset_password_token, *args, **kwargs
):
    """
    Handles password reset tokens
    When a token is created, an e-mail needs to be sent to the user
    :param sender: View Class that sent the signal
    :param instance: View Instance that sent the signal
    :param reset_password_token: Token Model Object
    :param args:
    :param kwargs:
    :return:
    """

    # send an e-mail to the user
    context = {
        "current_user": reset_password_token.user,
        "email": reset_password_token.user.email,
        "reset_password_url": "{}?token={}".format(
            FRONTEND_URL,
            reset_password_token.key,
        ),
    }

    # render email text
    email_html_message = render_to_string("./email/user_reset_password.html", context)
    email_plaintext_message = render_to_string(
        "./email/user_reset_password.txt", context
    )

    msg = EmailMultiAlternatives(
        # title:
        "Password Reset for {title}".format(title="Cards"),
        # message:
        email_plaintext_message,
        # from:
        DEFAULT_FROM_EMAIL,
        # to:
        [reset_password_token.user.email],
    )
    msg.attach_alternative(email_html_message, "text/html")
    msg.send()


@receiver(post_save, sender=UserSocialAuth, dispatch_uid="create_profile_for_google_auth")
def create_profile_for_google_auth(sender, instance, created, **kwargs):
    # social_django will request extra_data from google after UserSocialAuth has been created.
    # for google provider, if extra_data has "access_token" it does mean that request extra_data has been called.
    if (
        getattr(settings, "SOCIAL_AUTH_AUTO_CREATE_PROFILE", False)
        and not instance.user.get_profile()
        and instance.provider == "google-oauth2"
        and instance.extra_data.get("access_token")
    ):
        extra_data = instance.extra_data
        _, _ = Profile.objects.create(
            user=instance.user,
            first_name=extra_data.get("given_name", "Unknown"),
            last_name=extra_data.get("family_name", "Unknown"),
        )

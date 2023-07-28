from django.db.models.signals import post_save
from django.dispatch import receiver
from comm_manager.models import ChatUser
from comm_manager.tasks import get_profile_for_user
import os


@receiver(post_save, sender=ChatUser)
def auto_fetch_profile(sender, instance, created, **kwargs):
    if created and not os.environ.get("TEST", False):
        get_profile_for_user.delay(instance.external_id)

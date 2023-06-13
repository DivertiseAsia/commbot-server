import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _


class Chat(models.Model):
    class ChatType(models.IntegerChoices):
        INDIVIDUAL = 1
        GROUP = 2

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    chat_type = models.IntegerField(choices=ChatType.choices)
    joined_date = models.DateTimeField(_("Joined Date"), auto_now_add=True)
    ended_date = models.DateTimeField(blank=True, null=True)
    external_id = models.CharField(
        _("External ID (from Provider)"), max_length=255, blank=True, db_index=True
    )
    is_mirrorreply_feature_on = models.BooleanField(default=False)
    # TODO: current members
    # TODO: lifetime members

import uuid
from typing import Any, Tuple

from django.db import models
from django.utils.translation import gettext_lazy as _


class ChatUser(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    external_id = models.CharField(
        _("External ID (from Provider)"), max_length=255, blank=True, db_index=True
    )
    display_name = models.CharField(max_length=255, blank=True, null=True)
    last_pulled_date = models.DateTimeField(
        _("Last Pulled Via API Date"), blank=True, null=True
    )


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
    users = models.ManyToManyField(ChatUser, through="ChatMembership")


class ChatMembershipManager(models.Manager):
    def get_or_create_not_ended(
        self, chat: Chat, chat_user: ChatUser
    ) -> Tuple[Any, bool]:
        chat_memberships = chat.chatmembership_set.filter(
            chat_user=chat_user, ended_date__isnull=True
        )
        if chat_memberships.exists():
            return (chat_memberships.first(), False)
        else:
            new_membership = self.model(chat_user=chat_user, chat=chat)
            new_membership.save()
            return (new_membership, True)


class ChatMembership(models.Model):
    chat_user = models.ForeignKey(ChatUser, on_delete=models.CASCADE)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    first_seen_date = models.DateTimeField(_("First Seen Date"), auto_now_add=True)
    ended_date = models.DateTimeField(blank=True, null=True)

    objects = ChatMembershipManager()


class ChatMessage(models.Model):
    chat_user = models.ForeignKey(ChatUser, null=True, on_delete=models.SET_NULL)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    message = models.TextField()
    received_date = models.DateTimeField(_("Received Date"), auto_now_add=True)

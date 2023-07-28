from comm_manager.apis import handler, line_bot_api
from comm_manager.models import ChatUser, ChatMembership, Chat
from celery import shared_task
from django.utils import timezone


@shared_task
def get_profile_for_user(external_id: str):
    chat_user = ChatUser.objects.get(external_id=external_id)

    active_relationships = chat_user.chatmembership_set.filter(
        chat__ended_date__isnull=True, ended_date__isnull=True
    )

    groupchat_membership = active_relationships.filter(
        chat__chat_type=Chat.ChatType.GROUP,
    )
    if active_relationships.exists():
        if groupchat_membership.exists():
            groupchat_membership = groupchat_membership.first()
            profile = line_bot_api.get_group_member_profile(
                groupchat_membership.chat.external_id,
                external_id,
            )
        else:
            profile = line_bot_api.get_profile(external_id)

        chat_user.display_name = profile.display_name
        chat_user.last_pulled_date = timezone.now()
        chat_user.save()

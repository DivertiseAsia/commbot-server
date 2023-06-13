from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
import re
import time

from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent,
    TextMessage,
    TextSendMessage,
    FlexSendMessage,
    FollowEvent,
    UnfollowEvent,
    JoinEvent,
    LeaveEvent,
)
import json

from comm_manager.models import Chat
from comm_manager.apis import handler, line_bot_api


class CommViewSet(viewsets.GenericViewSet):
    @action(
        methods=["POST"],
        detail=False,
        url_path="webhook",
    )
    def webhook(self, request):
        # get X-Line-Signature header value
        try:
            signature = request.headers["X-Line-Signature"]
        except KeyError:
            return Response(
                "Missing X-Line-Signature header",
                status=status.HTTP_400_BAD_REQUEST,
            )

        # get request body as text
        body = request.body.decode("utf-8")

        # handle webhook body
        try:
            handler.handle(body, signature)
        except InvalidSignatureError:
            return Response(
                "Invalid signature. Please check your channel access token/channel secret.",
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(status=status.HTTP_200_OK)


LOOKUP_DATA_VIA_API = re.compile(
    r"\[\[([^]]*)\]\]",
)


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    chat, _ = Chat.objects.get_or_create(
        external_id=event.source.user_id, chat_type=Chat.ChatType.INDIVIDUAL
    )
    message_text = event.message.text
    lookup_matches = LOOKUP_DATA_VIA_API.findall(message_text)
    if lookup_matches:
        from external_data_manager.helpers import (
            scryfall_search,
        )
        from .helpers import flex_json_card_image_with_price, carousel

        card_images = []
        card_alts = []
        for match in lookup_matches:
            card = scryfall_search(match)
            if card:
                card_alts.append(card.name + " " + card.mana_cost)
                card_images.append(
                    flex_json_card_image_with_price(card.image_url, card.price)
                )
            time.sleep(0.2)
        line_bot_api.reply_message(
            event.reply_token,
            FlexSendMessage(
                alt_text=", ".join(card_alts),
                contents=carousel(card_images),
            ),
        )
    elif chat.is_mirrorreply_feature_on:
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=message_text)
        )


@handler.add(FollowEvent)
def handle_followevent(event):
    Chat.objects.get_or_create(
        external_id=event.source.user_id, chat_type=Chat.ChatType.INDIVIDUAL
    )


@handler.add(UnfollowEvent)
def handle_unfollowevent(event):
    chat, _ = Chat.objects.get_or_create(
        external_id=event.source.user_id, chat_type=Chat.ChatType.INDIVIDUAL
    )
    chat.ended_date = timezone.now()
    chat.save()


@handler.add(JoinEvent)
def handle_joinevent(event):
    Chat.objects.get_or_create(
        external_id=event.source.group_id, chat_type=Chat.ChatType.GROUP
    )


@handler.add(LeaveEvent)
def handle_leaveevent(event):
    chat, _ = Chat.objects.get_or_create(
        external_id=event.source.group_id, chat_type=Chat.ChatType.GROUP
    )
    chat.ended_date = timezone.now()
    chat.save()

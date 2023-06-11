from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
import re

from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent,
    TextMessage,
    TextSendMessage,
    FlexSendMessage,
    FollowEvent,
    UnfollowEvent,
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
    message_text = event.message.text
    lookup_matches = LOOKUP_DATA_VIA_API.search(message_text)
    if lookup_matches:
        from external_data_manager.helpers import (
            scryfall_search,
            scryfall_first_card,
            scryfall_card_image,
            scryfall_card_price,
        )
        from .helpers import flex_json_card_image_with_price

        cards = scryfall_search(lookup_matches.group(1))
        card = scryfall_first_card(cards)
        image = scryfall_card_image(card)
        price = scryfall_card_price(card)
        line_bot_api.reply_message(
            event.reply_token,
            FlexSendMessage(
                alt_text="Some card",
                contents=flex_json_card_image_with_price(image, price),
            ),
        )
    else:
        Chat.objects.get_or_create(
            external_id=event.source.user_id, chat_type=Chat.ChatType.INDIVIDUAL
        )
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
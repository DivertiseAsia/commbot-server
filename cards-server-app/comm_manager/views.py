from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from django.conf import settings
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent,
    TextMessage,
    TextSendMessage,
    FlexSendMessage,
)

line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(settings.LINE_CHANNEL_SECRET)


class CommViewSet(viewsets.GenericViewSet):
    @action(
        methods=["POST"],
        detail=False,
        url_path="webhook",
    )
    def webhook(self, request):
        # get X-Line-Signature header value
        print("got webhook")
        try:
            signature = request.headers["X-Line-Signature"]
        except KeyError:
            return Response(
                "Missing X-Line-Signature header",
                status=status.HTTP_400_BAD_REQUEST,
            )

        # get request body as text
        body = request.body.decode("utf-8")
        print("body", body)

        # handle webhook body
        try:
            handler.handle(body, signature)
        except InvalidSignatureError:
            return Response(
                "Invalid signature. Please check your channel access token/channel secret.",
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(status=status.HTTP_200_OK)


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    if len(event.message.text) > 5:
        from external_data_manager.helpers import (
            scryfall_search,
            scryfall_first_card,
            scryfall_card_image,
            scryfall_card_price,
        )
        from helpers import flex_json_card_image_with_price

        cards = scryfall_search(event.message.text)
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
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=event.message.text)
        )

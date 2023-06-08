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


def flex_json_card_image_with_price(image, price):
    return {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "image",
                    "url": image,
                    "size": "full",
                    "aspectMode": "cover",
                    "aspectRatio": "7:10",
                    "gravity": "center",
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [],
                    "position": "absolute",
                    "background": {
                        "type": "linearGradient",
                        "angle": "0deg",
                        "endColor": "#00000000",
                        "startColor": "#00000099",
                    },
                    "width": "100%",
                    "height": "40%",
                    "offsetBottom": "0px",
                    "offsetStart": "0px",
                    "offsetEnd": "0px",
                },
                {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "Pricing",
                                            "size": "lg",
                                            "color": "#ffffff",
                                            "align": "end",
                                        }
                                    ],
                                },
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": f"${price}",
                                            "color": "#ffffff",
                                            "size": "md",
                                            "align": "end",
                                        }
                                    ],
                                },
                            ],
                            "spacing": "xs",
                        }
                    ],
                    "position": "absolute",
                    "offsetBottom": "50%",
                    "offsetStart": "50%",
                    "offsetEnd": "0px",
                    "paddingAll": "15px",
                    "paddingEnd": "22px",
                    "background": {
                        "type": "linearGradient",
                        "startColor": "#99999900",
                        "endColor": "#999999AA",
                        "centerColor": "#99999955",
                        "angle": "90deg",
                    },
                    "width": "50%",
                },
            ],
            "paddingAll": "0px",
        },
    }

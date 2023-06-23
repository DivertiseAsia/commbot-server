from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.shortcuts import render, get_object_or_404
import re
import time
from urllib.parse import unquote

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
    SourceGroup,
)
import json
import logging

from comm_manager.models import Chat
from comm_manager.apis import handler, line_bot_api
from comm_manager.forms import PushMessageForm

logger = logging.getLogger("comm_views")


class CommViewSet(viewsets.GenericViewSet):
    @action(detail=True, methods=["GET", "POST"], url_path="custom-form-view")
    def custom_form_view(self, request, pk=None):
        instance = get_object_or_404(Chat, id=pk)
        form = PushMessageForm()
        if request.method == "POST":
            form = PushMessageForm(request.POST)
            if form.is_valid():
                # Process the form data
                mt = form.cleaned_data["message_type"]
                if mt == "text":
                    line_bot_api.push_message(
                        instance.external_id,
                        TextSendMessage(text=form.cleaned_data["contents"]),
                    )
                else:
                    line_bot_api.push_message(
                        instance.external_id,
                        FlexSendMessage(
                            alt_text=form.cleaned_data["alt_text"],
                            contents=form.cleaned_data["contents"],
                        ),
                    )

        context = {
            "form": form,
            "instance": instance,
        }

        return render(
            request, "admin/comm_manager/chat/send_push_message_form.html", context
        )

    @action(
        methods=["GET"],
        detail=False,
        url_path="test",
    )
    def test(self, request):
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.firefox.launch()
            page = browser.new_page()
            page.goto("https://cardkingdom.com")
            title = page.title()
            browser.close()
            logger.info("title", title)
            return Response(title, status=status.HTTP_200_OK)

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
    ## TODO: Fix this. It cannot assume it's a individual chat... causes bugs
    logger.info(event)
    chat_id = event.source.user_id
    chat_type = Chat.ChatType.INDIVIDUAL
    if isinstance(event.source, SourceGroup):
        chat_id = event.source.group_id
        chat_type = Chat.ChatType.GROUP
    chat, _ = Chat.objects.get_or_create(external_id=chat_id, chat_type=chat_type)

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
                    flex_json_card_image_with_price(
                        card.image_url_ckd or card.image_url,
                        card.price_ckd,
                        unquote(card.url_ckd_search),
                    )
                )
            time.sleep(0.2)
        logger.info("card_json", card_images)
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

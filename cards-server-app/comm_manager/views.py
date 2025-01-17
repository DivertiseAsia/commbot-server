import json
import logging
import re
import time
from datetime import datetime
from urllib.parse import quote

from comm_manager.apis import handler, line_bot_api
from comm_manager.forms import PushMessageForm
from comm_manager.models import Chat, ChatMembership, ChatMessage, ChatUser
from django.contrib.sites.models import Site
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from event_manager.models import Event
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    FlexSendMessage,
    FollowEvent,
    JoinEvent,
    LeaveEvent,
    MemberJoinedEvent,
    MemberLeftEvent,
    MessageEvent,
    SourceGroup,
    TextMessage,
    TextSendMessage,
    UnfollowEvent,
)
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

logger = logging.getLogger("comm_views")


class CommViewSet(viewsets.GenericViewSet):
    @action(detail=False, methods=["get"], url_path="mtg-ckd-redirect")
    def mtg_ckd_redirect(self, request):
        from external_data_manager.models import MtgCard

        search = request.GET.get("search") or "Unknown Shores"

        return redirect(MtgCard.get_url_ckd_search(search))

    @action(detail=True, methods=["GET", "POST"], url_path="custom-form-view")
    def custom_form_view(self, request, pk=None):
        instance = get_object_or_404(Chat, id=pk)
        form = PushMessageForm()
        if request.method == "POST":
            form = PushMessageForm(request.POST)
            if form.is_valid():
                # Process the form data
                mt = form.cleaned_data["message_type"]
                message = TextSendMessage(
                    text="unhandled message type attempted to send"
                )
                if mt == "text":
                    message = TextSendMessage(text=form.cleaned_data["contents"])
                elif mt == "flex":
                    message_contents = json.loads(form.cleaned_data["contents"])
                    logger.warning("form contents", message_contents)
                    logger.warning("form contents type", type(message_contents))
                    message = FlexSendMessage(
                        alt_text=form.cleaned_data["alt_text"],
                        contents=message_contents,
                    )
                line_bot_api.push_message(instance.external_id, message)

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

    chat_user, _ = ChatUser.objects.get_or_create(external_id=event.source.user_id)

    ChatMembership.objects.get_or_create_not_ended(chat=chat, chat_user=chat_user)

    message_text = event.message.text
    ChatMessage.objects.create(message=message_text, chat_user=chat_user, chat=chat)
    lookup_matches = LOOKUP_DATA_VIA_API.findall(message_text)
    if lookup_matches:
        from external_data_manager.helpers import scryfall_search

        from .helpers import carousel, flex_json_card_image_with_price

        card_images = []
        card_alts = []
        for match in lookup_matches:
            card = scryfall_search(match)
            if card:
                card_alts.append(card.name + " " + card.mana_cost)
                relative_url = reverse("comm_manager:cvs-mtg-ckd-redirect")
                domain = Site.objects.get_current().domain
                full_url = f"https://{domain}{relative_url}?search={quote(card.name)}"

                card_images.append(
                    flex_json_card_image_with_price(
                        card.image_url_ckd or card.image_url,
                        card.price_ckd,
                        full_url,
                    )
                )
                if "pricing" in message_text.lower() or "price" in message_text.lower():
                    from external_data_manager.tasks import update_prices_for_card

                    update_prices_for_card.delay(card.pk, chat_id=chat_id)
            time.sleep(0.2)
        logger.info("card_json", card_images)
        line_bot_api.reply_message(
            event.reply_token,
            FlexSendMessage(
                alt_text=", ".join(card_alts),
                contents=carousel(card_images),
            ),
        )
    elif message_text == "!events":
        eqs = Event.objects.filter(date__gte=datetime.today().date()).order_by("date")
        event_list = []
        for e in eqs:
            event_list.append(str(e))
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text="\n".join(event_list))
        )
    elif chat.is_mirrorreply_feature_on:
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=message_text)
        )


@handler.add(FollowEvent)
def handle_followevent(event):
    (chat, created) = Chat.objects.get_or_create(
        external_id=event.source.user_id, chat_type=Chat.ChatType.INDIVIDUAL
    )
    if created:
        chat.users.create(external_id=event.source.user_id)


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


@handler.add(MemberJoinedEvent)
def handle_memberjoinedevent(event):
    chat = Chat.objects.get(external_id=event.source.group_id)

    chat_user, _ = ChatUser.objects.get_or_create(external_id=event.source.user_id)

    ChatMembership.objects.get_or_create_not_ended(chat=chat, chat_user=chat_user)


@handler.add(MemberLeftEvent)
def handle_memberleftevent(event):
    chat = Chat.objects.get(external_id=event.source.group_id)

    chat_user, _ = ChatUser.objects.get_or_create(external_id=event.source.user_id)
    if not ChatMembership.objects.filter(chat=chat, chat_user=chat_user).exists():
        ChatMembership.objects.create(
            chat=chat, chat_user=chat_user, ended_date=timezone.now()
        )
    else:
        ChatMembership.objects.filter(
            chat=chat, chat_user=chat_user, ended_date__isnull=True
        ).update(ended_date=timezone.now())

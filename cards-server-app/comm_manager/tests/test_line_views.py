from config.helpers import BaseTestCase
from comm_manager.models import Chat
from comm_manager.views import handle_followevent, handle_message, handle_unfollowevent
from unittest.mock import patch
import time


class TestLineViews(BaseTestCase):
    def setUp(self):
        super().setUp()

    def given_event_with_user_details_only(self, user_id):
        from munch import DefaultMunch

        undefined = object()
        return DefaultMunch.fromDict({"source": {"user_id": user_id}}, undefined)

    def given_message_event(self, message, user_id):
        from munch import DefaultMunch

        undefined = object()
        return DefaultMunch.fromDict(
            {"message": {"text": message}, "source": {"user_id": user_id}},
            undefined,
        )

    def test_user_follows_bot_first_time_creates_chat(self):
        self.assertEquals(0, Chat.objects.filter(external_id="abc").count())
        event = self.given_event_with_user_details_only("abc")

        handle_followevent(event)

        related_chat = Chat.objects.get(external_id="abc")
        self.assertEquals(related_chat.chat_type, Chat.ChatType.INDIVIDUAL)

    def test_user_follows_bot_twice_does_not_explode(self):
        self.assertEquals(0, Chat.objects.filter(external_id="abc").count())
        event = self.given_event_with_user_details_only("abc")

        handle_followevent(event)
        handle_followevent(event)

        self.assertEquals(1, Chat.objects.filter(external_id="abc").count())

    @patch("comm_manager.apis.line_bot_api.reply_message")
    def test_user_messages_bot_first_time_creates_chat_if_none_exists(self, mock):
        self.assertEquals(0, Chat.objects.filter(external_id="abc").count())
        event = self.given_message_event("msg", "abc")
        handle_message(event)

        related_chat = Chat.objects.get(external_id="abc")
        self.assertEquals(related_chat.chat_type, Chat.ChatType.INDIVIDUAL)

    @patch("comm_manager.apis.line_bot_api.reply_message")
    def test_user_messages_bot_later_time_does_not_make_a_second(self, mock):
        self.assertEquals(0, Chat.objects.filter(external_id="abc").count())
        event = self.given_message_event("msg", "abc")
        handle_message(event)

        time.sleep(0.1)
        handle_message(event)

        self.assertEquals(1, Chat.objects.filter(external_id="abc").count())

    def test_user_unfollows_bot_updates_chat(self):
        self.assertEquals(0, Chat.objects.filter(external_id="abc").count())
        event = self.given_event_with_user_details_only("abc")

        handle_followevent(event)

        related_chat = Chat.objects.get(external_id="abc")
        self.assertEquals(None, related_chat.ended_date)

        handle_unfollowevent(event)
        related_chat.refresh_from_db()
        self.assertNotEquals(None, related_chat.ended_date)

    def test_user_unfollows_bot_without_follow_does_not_explode(self):
        self.assertEquals(0, Chat.objects.filter(external_id="abc").count())
        event = self.given_event_with_user_details_only("abc")

        handle_unfollowevent(event)
        related_chat = Chat.objects.get(external_id="abc")
        self.assertNotEquals(None, related_chat.ended_date)

    # TODO group related ones

    @patch("external_data_manager.helpers.scryfall_search")
    @patch("comm_manager.apis.line_bot_api.reply_message")
    def test_user_messages_bot_without_card_search_and_does_not_hit_scryfall(
        self, mock_reply, mock_scryfall
    ):
        event = self.given_message_event("msg", "abcd")
        handle_message(event)
        assert not mock_scryfall.called
        assert mock_reply.called

import time
from unittest.mock import MagicMock, call, patch

from comm_manager.models import Chat, ChatMembership, ChatMessage, ChatUser
from comm_manager.views import (
    handle_followevent,
    handle_joinevent,
    handle_leaveevent,
    handle_memberjoinedevent,
    handle_memberleftevent,
    handle_message,
    handle_unfollowevent,
)
from config.helpers import BaseTestCase
from django.utils import timezone
from linebot.models import SourceGroup, SourceUser


class TestLineViews(BaseTestCase):
    def setUp(self):
        super().setUp()

    def given_event_with_user_details_only(self, user_id):
        basic = MagicMock()
        basic.source = SourceUser(user_id=user_id)
        return basic

    def given_message_event(self, message, user_id):
        from munch import DefaultMunch

        undefined = object()
        munch = DefaultMunch.fromDict(
            {
                "message": {"text": message},
            },
            undefined,
        )
        munch.source = SourceUser(user_id=user_id)
        return munch

    def given_message_event_in_group(self, message, user_id, group_id):
        from munch import DefaultMunch

        undefined = object()
        munch = DefaultMunch.fromDict(
            {
                "message": {"text": message},
            },
            undefined,
        )
        munch.source = SourceGroup(user_id=user_id, group_id=group_id)
        return munch

    def given_event_with_group_details(self, message, user_id, group_id):
        from munch import DefaultMunch

        undefined = object()
        return DefaultMunch.fromDict(
            {
                "message": {"text": message},
                "source": {"user_id": user_id, "group_id": group_id},
            },
            undefined,
        )

    def test_user_follows_bot_first_time_creates_chat(self):
        self.assertEquals(0, Chat.objects.filter(external_id="abc").count())
        event = self.given_event_with_user_details_only("abc")

        handle_followevent(event)

        related_chat = Chat.objects.get(external_id="abc")
        self.assertEquals(related_chat.chat_type, Chat.ChatType.INDIVIDUAL)
        self.assertEquals(1, related_chat.users.count())
        related_chat_user = related_chat.users.first()
        self.assertEquals("abc", related_chat_user.external_id)
        self.assertEquals(None, related_chat_user.display_name)

    def test_user_follows_bot_twice_does_not_explode(self):
        self.assertEquals(0, Chat.objects.filter(external_id="abc").count())
        event = self.given_event_with_user_details_only("abc")

        handle_followevent(event)
        handle_followevent(event)

        chat = Chat.objects.get(external_id="abc")
        self.assertEquals(1, chat.users.count())

    @patch("comm_manager.apis.line_bot_api.reply_message")
    def test_user_messages_bot_first_time_creates_chat_if_none_exists(self, mock):
        self.assertEquals(0, Chat.objects.filter(external_id="abc").count())
        event = self.given_message_event("msg", "abc")
        handle_message(event)

        related_chat = Chat.objects.get(external_id="abc")
        self.assertEquals(related_chat.chat_type, Chat.ChatType.INDIVIDUAL)

    @patch("external_data_manager.helpers.scryfall_search")
    @patch("comm_manager.apis.line_bot_api.reply_message")
    def test_user_messages_bot_first_time_creates_chat_if_none_exists_event_as_search(
        self, mock, mock_scryfall
    ):
        mock_scryfall.return_value = None
        self.assertEquals(0, Chat.objects.filter(external_id="abc").count())
        event = self.given_message_event("[[msg]]", "abc")
        handle_message(event)

        related_chat = Chat.objects.get(external_id="abc")
        self.assertEquals(related_chat.chat_type, Chat.ChatType.INDIVIDUAL)

    @patch("external_data_manager.helpers.scryfall_search")
    @patch("comm_manager.apis.line_bot_api.reply_message")
    def test_user_messages_bot_first_time_from_group_creates_chat_if_none_exists_event_as_search(
        self, mock, mock_scryfall
    ):
        mock_scryfall.return_value = None
        self.assertEquals(0, Chat.objects.filter(external_id="groupA").count())
        event = self.given_message_event_in_group("[[msg]]", "abc", "groupA")
        handle_message(event)

        related_chat = Chat.objects.get(external_id="groupA")
        self.assertEquals(related_chat.chat_type, Chat.ChatType.GROUP)
        related_chat_user = related_chat.users.first()
        self.assertEquals("abc", related_chat_user.external_id)
        self.assertEquals(None, related_chat_user.display_name)

    @patch("external_data_manager.helpers.scryfall_search")
    @patch("comm_manager.apis.line_bot_api.reply_message")
    def test_user_messages_bot_from_group_after_leaving_group_creates_new_membership(
        self, mock, mock_scryfall
    ):
        mock_scryfall.return_value = None
        self.assertEquals(0, Chat.objects.filter(external_id="groupA").count())
        intial_chat_users = ChatUser.objects.all().count()
        event = self.given_message_event_in_group("[[msg]]", "abc", "groupA")
        handle_message(event)

        self.assertEquals(intial_chat_users + 1, ChatUser.objects.all().count())
        related_chat = Chat.objects.get(external_id="groupA")
        self.assertEquals(1, related_chat.chatmembership_set.all().count())
        first_membership = related_chat.chatmembership_set.first()

        self.assertEquals(None, first_membership.ended_date)
        first_membership.ended_date = timezone.now()
        first_membership.save()

        handle_message(event)

        self.assertEquals(intial_chat_users + 1, ChatUser.objects.all().count())
        self.assertEquals(2, related_chat.chatmembership_set.all().count())

        handle_message(event)
        self.assertEquals(2, related_chat.chatmembership_set.all().count())

    @patch("comm_manager.apis.line_bot_api.reply_message")
    def test_user_messages_bot_later_time_does_not_make_a_second(self, mock):
        self.assertEquals(0, Chat.objects.filter(external_id="abc").count())
        initial_chat_users = ChatUser.objects.all().count()
        event = self.given_message_event("msg", "abc")
        handle_message(event)

        time.sleep(0.1)
        handle_message(event)

        related_chats = Chat.objects.filter(external_id="abc")
        self.assertEquals(1, related_chats.count())
        self.assertEquals(1, related_chats.first().users.count())
        self.assertEquals(initial_chat_users + 1, ChatUser.objects.all().count())
        self.assertEquals(1, related_chats.first().chatmembership_set.all().count())

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
        c = Chat.objects.create(
            external_id="userid1",
            chat_type=Chat.ChatType.INDIVIDUAL,
            is_mirrorreply_feature_on=True,
        )
        c.save()
        event = self.given_message_event("This is a decently long message", "userid1")
        handle_message(event)
        assert not mock_scryfall.called
        assert mock_reply.called

    @patch("external_data_manager.helpers.scryfall_search")
    @patch("comm_manager.apis.line_bot_api.reply_message")
    def test_user_messages_bot_with_card_search_and_will_hit_scryfall(
        self, mock_reply, mock_scryfall
    ):
        mock_scryfall.return_value = None
        event = self.given_message_event(
            "This will hit scryfall with [[something]]", "userid1"
        )
        handle_message(event)
        mock_scryfall.assert_called_once_with("something")
        assert mock_reply.called

    @patch("external_data_manager.helpers.scryfall_search")
    @patch("comm_manager.apis.line_bot_api.reply_message")
    def test_user_messages_bot_with_multiple_card_search_and_will_hit_scryfall(
        self, mock_reply, mock_scryfall
    ):
        mock_scryfall.return_value = None
        event = self.given_message_event(
            "This will hit scryfall with [[something]] [[dog]]", "userid1"
        )
        handle_message(event)
        mock_scryfall.assert_has_calls([call("something"), call("dog")], any_order=True)
        mock_reply.assert_called_once()

    @patch("comm_manager.apis.line_bot_api.reply_message")
    def test_user_invites_bot_to_group_chat_creates_chat_if_none_exists(self, mock):
        self.assertEquals(0, Chat.objects.filter(external_id="group1").count())
        event = self.given_event_with_group_details("msg", "abc", "group1")
        handle_joinevent(event)

        related_chat = Chat.objects.get(external_id="group1")
        self.assertEquals(related_chat.chat_type, Chat.ChatType.GROUP)

    @patch("comm_manager.apis.line_bot_api.reply_message")
    def test_user_invites_bot_to_group_chat_does_not_explode_if_done_twice(self, mock):
        self.assertEquals(0, Chat.objects.filter(external_id="group1").count())
        event = self.given_event_with_group_details("msg", "abc", "group1")
        handle_joinevent(event)

        self.assertEquals(1, Chat.objects.filter(external_id="group1").count())
        handle_joinevent(event)
        self.assertEquals(1, Chat.objects.filter(external_id="group1").count())

    @patch("comm_manager.apis.line_bot_api.reply_message")
    def test_leaves_group_chat_does_not_explode_if_done_twice(self, mock):
        event = self.given_event_with_group_details("msg", "abc", "group1")
        handle_joinevent(event)

        chat = Chat.objects.get(external_id="group1")
        self.assertEquals(None, chat.ended_date)

        handle_leaveevent(event)

        chat.refresh_from_db()
        self.assertNotEquals(None, chat.ended_date)

        handle_leaveevent(event)
        self.assertEquals(1, Chat.objects.filter(external_id="group1").count())

    @patch("comm_manager.apis.line_bot_api.reply_message")
    def test_leaves_group_chat_does_not_explode_no_existing_chat(self, mock):
        self.assertEquals(0, Chat.objects.filter(external_id="group1").count())
        event = self.given_event_with_group_details("msg", "abc", "group1")

        handle_leaveevent(event)

        chat = Chat.objects.get(external_id="group1")
        self.assertNotEquals(None, chat.ended_date)

    @patch("comm_manager.apis.line_bot_api.reply_message")
    def test_user_normal_messages_bot_if_mirrorreply_off_skips(self, mock):
        c = Chat.objects.create(
            external_id="abc",
            chat_type=Chat.ChatType.INDIVIDUAL,
            is_mirrorreply_feature_on=False,
        )
        c.save()
        event = self.given_message_event("msg", "abc")
        handle_message(event)

        assert not mock.called

    def test_new_person_joins_group_chat_they_have_first_membership(self):
        given_user_id = "abc"
        given_chat_id = "group1"
        Chat.objects.create(external_id=given_chat_id, chat_type=Chat.ChatType.GROUP)
        self.assertEquals(0, ChatUser.objects.filter(external_id=given_user_id).count())
        event = self.given_event_with_group_details("msg", given_user_id, given_chat_id)

        handle_memberjoinedevent(event)

        chat = Chat.objects.get(external_id=given_chat_id)
        chat_user = ChatUser.objects.get(external_id=given_user_id)
        self.assertEquals(
            1, ChatMembership.objects.filter(chat=chat, chat_user=chat_user).count()
        )

    def test_existing_person_joins_group_chat_they_have_first_membership(self):
        given_user_id = "abc"
        given_chat_id = "group1"
        Chat.objects.create(external_id=given_chat_id, chat_type=Chat.ChatType.GROUP)
        ChatUser.objects.create(external_id=given_user_id)
        event = self.given_event_with_group_details("msg", given_user_id, given_chat_id)

        handle_memberjoinedevent(event)

        chat = Chat.objects.get(external_id=given_chat_id)
        chat_user = ChatUser.objects.get(external_id=given_user_id)
        self.assertEquals(
            1, ChatMembership.objects.filter(chat=chat, chat_user=chat_user).count()
        )

    def test_existing_person_REjoins_group_chat_they_had_preexisting_membership(self):
        given_user_id = "abc"
        given_chat_id = "group1"
        chat = Chat.objects.create(
            external_id=given_chat_id, chat_type=Chat.ChatType.GROUP
        )
        chat_user = ChatUser.objects.create(external_id=given_user_id)
        ChatMembership.objects.create(
            chat=chat, chat_user=chat_user, ended_date=timezone.now()
        )

        event = self.given_event_with_group_details("msg", given_user_id, given_chat_id)

        handle_memberjoinedevent(event)

        self.assertEquals(
            2, ChatMembership.objects.filter(chat=chat, chat_user=chat_user).count()
        )

    def test_existing_person_joins_group_chat_twice_fired_doesnt_create_bad_data(self):
        given_user_id = "abc"
        given_chat_id = "group1"
        chat = Chat.objects.create(
            external_id=given_chat_id, chat_type=Chat.ChatType.GROUP
        )
        chat_user = ChatUser.objects.create(external_id=given_user_id)
        ChatMembership.objects.create(chat=chat, chat_user=chat_user)

        event = self.given_event_with_group_details("msg", given_user_id, given_chat_id)

        handle_memberjoinedevent(event)
        handle_memberjoinedevent(event)

        self.assertEquals(
            1, ChatMembership.objects.filter(chat=chat, chat_user=chat_user).count()
        )

    def test_notexisting_person_leaving_group_chat_without_membership_still_saves_them(
        self,
    ):
        given_user_id = "abc"
        given_chat_id = "group1"
        chat = Chat.objects.create(
            external_id=given_chat_id, chat_type=Chat.ChatType.GROUP
        )

        event = self.given_event_with_group_details("msg", given_user_id, given_chat_id)

        handle_memberleftevent(event)

        membership = ChatMembership.objects.get(
            chat=chat, chat_user=ChatUser.objects.get(external_id=given_user_id)
        )

        self.assertNotEquals(None, membership.ended_date)

    def test_existing_person_leaves_group_chat_they_had_preexisting_membership(self):
        given_user_id = "abc"
        given_chat_id = "group1"
        chat = Chat.objects.create(
            external_id=given_chat_id, chat_type=Chat.ChatType.GROUP
        )
        chat_user = ChatUser.objects.create(external_id=given_user_id)
        ChatMembership.objects.create(
            chat=chat, chat_user=chat_user, ended_date=timezone.now()
        )

        event = self.given_event_with_group_details("msg", given_user_id, given_chat_id)

        handle_memberleftevent(event)

        membership = ChatMembership.objects.get(chat=chat, chat_user=chat_user)

        self.assertNotEquals(None, membership.ended_date)

    def test_existing_person_leaves_group_chat_firing_twice_does_not_cause_data_error(
        self,
    ):
        given_user_id = "abc"
        given_chat_id = "group1"
        chat = Chat.objects.create(
            external_id=given_chat_id, chat_type=Chat.ChatType.GROUP
        )
        chat_user = ChatUser.objects.create(external_id=given_user_id)
        ChatMembership.objects.create(
            chat=chat, chat_user=chat_user, ended_date=timezone.now()
        )

        event = self.given_event_with_group_details("msg", given_user_id, given_chat_id)

        handle_memberleftevent(event)
        handle_memberleftevent(event)

        membership = ChatMembership.objects.get(chat=chat, chat_user=chat_user)

        self.assertNotEquals(None, membership.ended_date)

    def test_existing_person_leaves_group_chat_twice_does_not_update_old_one(
        self,
    ):
        given_user_id = "abc"
        given_chat_id = "group1"
        chat = Chat.objects.create(
            external_id=given_chat_id, chat_type=Chat.ChatType.GROUP
        )
        chat_user = ChatUser.objects.create(external_id=given_user_id)
        ChatMembership.objects.create(
            chat=chat, chat_user=chat_user, ended_date=timezone.now()
        )

        event = self.given_event_with_group_details("msg", given_user_id, given_chat_id)

        handle_memberleftevent(event)

        time.sleep(0.1)

        handle_memberjoinedevent(event)

        handle_memberleftevent(event)

        memberships = ChatMembership.objects.filter(chat=chat, chat_user=chat_user)
        self.assertEquals(2, memberships.count())

        self.assertNotEquals(
            memberships.first().ended_date, memberships.last().ended_date
        )

    def test_message_in_group_chat_saved_as_message(self):
        message = "hi"
        user_id = "abc"
        group_id = "groupA"
        event = self.given_message_event_in_group(message, user_id, group_id)

        handle_message(event)

        related_chat = Chat.objects.get(external_id=group_id)
        related_user = ChatUser.objects.get(external_id=user_id)

        cm = ChatMessage.objects.get(chat=related_chat, chat_user=related_user)
        self.assertEquals(cm.message, message)

        second_message = "this is number two"
        event_two = self.given_message_event_in_group(second_message, user_id, group_id)
        handle_message(event_two)

        self.assertEquals(
            2,
            ChatMessage.objects.filter(
                chat=related_chat, chat_user=related_user
            ).count(),
        )
        self.assertTrue(
            ChatMessage.objects.filter(
                chat=related_chat, chat_user=related_user, message=second_message
            ).exists()
        )

    def test_message_in_one_on_one_chat_saved_as_message(self):
        message = "hi"
        user_id = "abc"
        event = self.given_message_event(message, user_id)

        handle_message(event)

        related_chat = Chat.objects.get(external_id=user_id)
        related_user = ChatUser.objects.get(external_id=user_id)

        cm = ChatMessage.objects.get(chat=related_chat, chat_user=related_user)
        self.assertEquals(cm.message, message)

        second_message = "this is number two"
        event_two = self.given_message_event(second_message, user_id)
        handle_message(event_two)

        self.assertEquals(
            2,
            ChatMessage.objects.filter(
                chat=related_chat, chat_user=related_user
            ).count(),
        )
        self.assertTrue(
            ChatMessage.objects.filter(
                chat=related_chat, chat_user=related_user, message=second_message
            ).exists()
        )

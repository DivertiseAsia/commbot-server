from config.helpers import BaseTestCase
from comm_manager.models import Chat, ChatUser, ChatMembership
from linebot.models import Profile
from unittest.mock import patch, call, ANY, MagicMock
import time
from django.utils import timezone
from comm_manager.tasks import get_profile_for_user


class TestTasks(BaseTestCase):
    def setUp(self):
        super().setUp()

    @patch("comm_manager.apis.line_bot_api.get_group_member_profile")
    @patch("comm_manager.apis.line_bot_api.get_profile")
    def test_user_does_not_exist_throws_error(
        self, mock_get_profile, mock_get_group_member_profile
    ):
        chat_user_dne_id = "doesnotexist"
        ChatUser.objects.filter(external_id=chat_user_dne_id)
        threw_exception = False
        try:
            get_profile_for_user(chat_user_dne_id)
        except Exception as e:
            threw_exception = True
            self.assertNotEquals(None, e)

        self.assertTrue(threw_exception)
        assert not mock_get_profile.called
        assert not mock_get_group_member_profile.called

    @patch("comm_manager.apis.line_bot_api.get_group_member_profile")
    @patch("comm_manager.apis.line_bot_api.get_profile")
    def test_user_without_active_chat_membership_does_not_call_api(
        self, mock_get_profile, mock_get_group_member_profile
    ):
        chat_user_id = "abc123"
        chat = Chat.objects.create(
            chat_type=Chat.ChatType.GROUP, external_id="irrelevant"
        )
        chat_user = ChatUser.objects.create(external_id=chat_user_id)
        ChatMembership.objects.create(
            chat=chat, chat_user=chat_user, ended_date=timezone.now()
        )
        old_individual_chat = Chat.objects.create(
            chat_type=Chat.ChatType.INDIVIDUAL,
            external_id="oldindividual",
            ended_date=timezone.now(),
        )
        ChatMembership.objects.create(chat=old_individual_chat, chat_user=chat_user)

        get_profile_for_user(chat_user_id)

        assert not mock_get_profile.called
        assert not mock_get_group_member_profile.called

    @patch("comm_manager.apis.line_bot_api.get_group_member_profile")
    @patch("comm_manager.apis.line_bot_api.get_profile")
    def test_user_with_active_individual_chat_calls_profile_api(
        self, mock_get_profile, mock_get_group_member_profile
    ):
        expected_display_name = "test"
        mock_get_profile.return_value = Profile(display_name=expected_display_name)

        chat_user_id = "abc123"
        chat = Chat.objects.create(
            chat_type=Chat.ChatType.INDIVIDUAL, external_id="irrelevant"
        )
        chat_user = ChatUser.objects.create(external_id=chat_user_id)
        ChatMembership.objects.create(chat=chat, chat_user=chat_user)

        get_profile_for_user(chat_user_id)

        mock_get_profile.assert_called_once_with(chat_user_id)
        assert not mock_get_group_member_profile.called

        chat_user.refresh_from_db()
        self.assertEquals(expected_display_name, chat_user.display_name)
        self.assertNotEquals(None, chat_user.last_pulled_date)

    @patch("comm_manager.apis.line_bot_api.get_group_member_profile")
    @patch("comm_manager.apis.line_bot_api.get_profile")
    def test_user_with_active_chat_group_membership_calls_group_api(
        self, mock_get_profile, mock_get_group_member_profile
    ):
        expected_display_name = "Dog"
        mock_get_group_member_profile.return_value = Profile(
            display_name=expected_display_name
        )

        chat_user_id = "abc123"
        group_id = "def123"
        chat = Chat.objects.create(chat_type=Chat.ChatType.GROUP, external_id=group_id)
        chat_user = ChatUser.objects.create(external_id=chat_user_id)
        ChatMembership.objects.create(chat=chat, chat_user=chat_user)

        get_profile_for_user(chat_user_id)

        assert not mock_get_profile.called
        mock_get_group_member_profile.assert_called_once_with(group_id, chat_user_id)

        chat_user.refresh_from_db()
        self.assertEquals(expected_display_name, chat_user.display_name)
        self.assertNotEquals(None, chat_user.last_pulled_date)

    @patch("comm_manager.apis.line_bot_api.get_group_member_profile")
    @patch("comm_manager.apis.line_bot_api.get_profile")
    def test_user_with_multiple_chats_calls_through_active_group_for_user_api(
        self, mock_get_profile, mock_get_group_member_profile
    ):
        expected_display_name = "cat"
        mock_get_group_member_profile.return_value = Profile(
            display_name=expected_display_name
        )

        chat_user_id = "abc123"
        chat_user = ChatUser.objects.create(external_id=chat_user_id)
        first_group_id = "group1"
        second_group_id = "group2"

        old_chat = Chat.objects.create(
            chat_type=Chat.ChatType.GROUP, external_id=first_group_id
        )
        first_group_membership = ChatMembership.objects.create(
            chat=old_chat, chat_user=chat_user, ended_date=timezone.now()
        )
        new_group_chat = Chat.objects.create(
            chat_type=Chat.ChatType.GROUP,
            external_id=second_group_id,
        )
        second_group_membership = ChatMembership.objects.create(
            chat=new_group_chat, chat_user=chat_user
        )

        get_profile_for_user(chat_user_id)
        assert not mock_get_profile.called
        mock_get_group_member_profile.assert_called_once_with(
            second_group_id, chat_user_id
        )

        first_group_membership.ended_date = None
        first_group_membership.save()
        second_group_membership.ended_date = timezone.now()
        second_group_membership.save()

        get_profile_for_user(chat_user_id)
        assert not mock_get_profile.called
        mock_get_group_member_profile.assert_called_with(first_group_id, chat_user_id)

        chat_user.refresh_from_db()
        self.assertEquals(expected_display_name, chat_user.display_name)
        self.assertNotEquals(None, chat_user.last_pulled_date)

    @patch("comm_manager.apis.line_bot_api.get_group_member_profile")
    @patch("comm_manager.apis.line_bot_api.get_profile")
    def test_user_with_multiple_chats_calls_through_active_group_for_bot_api(
        self, mock_get_profile, mock_get_group_member_profile
    ):
        expected_display_name = "cat"
        mock_get_group_member_profile.return_value = Profile(
            display_name=expected_display_name
        )

        chat_user_id = "abc123"
        chat_user = ChatUser.objects.create(external_id=chat_user_id)
        first_group_id = "group1"
        second_group_id = "group2"

        old_chat = Chat.objects.create(
            chat_type=Chat.ChatType.GROUP,
            external_id=first_group_id,
            ended_date=timezone.now(),
        )
        first_group_membership = ChatMembership.objects.create(
            chat=old_chat, chat_user=chat_user
        )
        new_group_chat = Chat.objects.create(
            chat_type=Chat.ChatType.GROUP,
            external_id=second_group_id,
        )
        second_group_membership = ChatMembership.objects.create(
            chat=new_group_chat, chat_user=chat_user
        )

        get_profile_for_user(chat_user_id)
        assert not mock_get_profile.called
        mock_get_group_member_profile.assert_called_once_with(
            second_group_id, chat_user_id
        )

        old_chat.ended_date = None
        old_chat.save()
        new_group_chat.ended_date = timezone.now()
        new_group_chat.save()

        get_profile_for_user(chat_user_id)
        assert not mock_get_profile.called
        mock_get_group_member_profile.assert_called_with(first_group_id, chat_user_id)

        chat_user.refresh_from_db()
        self.assertEquals(expected_display_name, chat_user.display_name)
        self.assertNotEquals(None, chat_user.last_pulled_date)

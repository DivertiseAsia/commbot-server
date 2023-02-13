# """
# Demo Manager's Slow API Alert
# """
from unittest.mock import patch
from django.core import mail
from django.test import override_settings
from rest_framework.reverse import reverse

from config.helpers import BaseTestCase
from demo_manager.models import Author, Book


class TestSlowApiAlertTriggered(BaseTestCase):


    def get_book_list_first_page(self):
        self.given_url(reverse(f"demo:books-list"))
        self.given_query_params({"page": 1})

        self.when_user_gets_json()

    @patch("config.middleware.slow_api.slow_api_alert_triggered.send")
    @override_settings(SLOW_API_ALERT_AT_MS=30000)
    def test_signal_not_triggered_when_get_book_list_with_valid_page_time_to_response_as_expected(self, mock_signal_send):
        self.get_book_list_first_page()

        self.assertResponseSuccess()
        self.assertFalse(mock_signal_send.called)
        print(">> test_signal_not_triggered_when_get_book_list_with_valid_page_time_to_response_as_expected: OK <<")

    @patch("config.middleware.slow_api.slow_api_alert_triggered.send")
    @override_settings(SLOW_API_ALERT_AT_MS=1)
    def test_signal_triggered_when_get_book_list_with_valid_page_took_too_much_time_to_response(self, mock_signal_send):
        self.get_book_list_first_page()

        self.assertResponseSuccess()
        self.assertTrue(mock_signal_send.called)
        print(f">>> mock_signal_send.call_args[1]: {mock_signal_send.call_args[1]}")

        print(">> test_signal_triggered_when_get_book_list_with_valid_page_took_too_much_time_to_response: OK <<")

    @override_settings(SLOW_API_ALERT_AT_MS=30000)
    def test_alert_email_not_sent_when_get_book_list_with_valid_page_time_to_response_as_expected(self):
        self.get_book_list_first_page()

        self.assertResponseSuccess()
        self.assertEqual(len(mail.outbox), 0)
        print(">> test_alert_email_not_sent_when__get_book_list_with_valid_page_time_to_response_as_expected: OK <<")

    @override_settings(SLOW_API_ALERT_AT_MS=1)
    def test_alert_email_sent_when_get_book_list_with_valid_page_took_too_much_time_to_response(self):
        self.get_book_list_first_page()

        self.assertResponseSuccess()
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "[Alert] Slow API detected")
        print(">> test_alert_email_sent_when_get_book_list_with_valid_page_took_too_much_time_to_response: OK <<")

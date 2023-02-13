# """
# Slow API Alert Middleware
# """
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import override_settings
from rest_framework.reverse import reverse

from config.helpers import BaseTestCase

User = get_user_model()


class TestSlowApiAlertMiddleware(BaseTestCase):

    def get_book_list_first_page(self):
        self.given_url(reverse(f"demo:books-list"))
        self.given_query_params({"page": 1})

        self.when_user_gets_json()

    @patch("config.middleware.slow_api.slow_api_alert_triggered.send")
    @override_settings(SLOW_API_ALERT_AT_MS=30000)
    def test_signal_not_triggered_when_get_book_list_with_valid_page_time_to_response_as_expected(self,
                                                                                                  mock_signal_send):
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

        print(">> test_signal_triggered_when_get_book_list_with_valid_page_took_too_much_time_to_response: OK <<")

# """
# Demo Manager's Slow API Alert
# """
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import override_settings
from rest_framework.reverse import reverse

from config.helpers import BaseTestCase

User = get_user_model()


class TestSlowApiAlertTriggered(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.staff_user = User.objects.create(email="staffuser@mockup.test", is_superuser=True)

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

    @override_settings(SLOW_API_ALERT_AT_MS=30000)
    def test_alert_email_not_sent_when_get_book_list_with_valid_page_time_to_response_as_expected(self):
        self.get_book_list_first_page()

        self.assertResponseSuccess()
        self.assertEqual(len(mail.outbox), 0)
        print(">> test_alert_email_not_sent_when__get_book_list_with_valid_page_time_to_response_as_expected: OK <<")

    @override_settings(SLOW_API_ALERT_AT_MS=0.001)
    def test_alert_email_sent_when_get_book_list_with_valid_page_took_time_to_response_more_than_expected(self):
        self.get_book_list_first_page()

        self.assertResponseSuccess()
        self.assertEqual(len(mail.outbox), 1)
        alert_email = mail.outbox[0]
        self.assertEqual(alert_email.subject, "[Alert] Slow API detected")
        self.assertIn(self.staff_user.email, alert_email.to)
        print(">> test_alert_email_sent_when_get_book_list_with_valid_page_took_time_to_response_more_than_expected: "
              "OK <<")

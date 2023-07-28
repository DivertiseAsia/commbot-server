# """
# Failed API Alert Middleware
# """
from unittest.mock import patch

from config.helpers import BaseTestCase
from django.contrib.auth import get_user_model
from django.test import override_settings
from rest_framework.reverse import reverse

User = get_user_model()


class TestFailedApiAlertMiddleware(BaseTestCase):
    @staticmethod
    def get_mockup_register_payload():
        return {
            "email": "test_middleware_user@divertise.asia",
            "password": "@somerandomPassword",
            "confirm_password": "@somerandomPassword",
            "profile": {
                "first_name": "test_middleware_user",
                "last_name": "divertise",
            },
        }

    @patch("config.middleware.failed_api.failed_api_alert_triggered.send")
    @override_settings(
        FAILED_API_ALERT_STATUS_CODES=[400], FAILED_API_ALERT_NAMESPACES=["v1"]
    )
    def test_signal_not_triggered_when_register_success_w_201_status_code(
        self, mock_signal_send
    ):
        self.given_url(reverse("v1:auth-register"))

        self.when_user_posts(self.get_mockup_register_payload())

        self.assertResponseCreated()
        self.assertFalse(mock_signal_send.called)

    @patch("config.middleware.failed_api.failed_api_alert_triggered.send")
    @override_settings(
        FAILED_API_ALERT_STATUS_CODES=[400], FAILED_API_ALERT_NAMESPACES=["v1"]
    )
    def test_signal_triggered_when_register_failed_w_400_status_code_there_no_password_in_payload(
        self, mock_signal_send
    ):
        self.given_url(reverse("v1:auth-register"))

        payload = self.get_mockup_register_payload()
        _password = payload.pop("password")

        self.when_user_posts(payload)

        self.assertResponseBadRequest()
        self.assertTrue(mock_signal_send.called)

# """
# Slow API Alert Middleware
# """
from unittest.mock import patch

from config.helpers import BaseTestCase
from django.contrib.auth import get_user_model
from django.test import override_settings
from rest_framework.reverse import reverse

User = get_user_model()


class TestSlowApiAlertMiddleware(BaseTestCase):
    def get_healthcheck_detail(self):
        self.response = self.client.get("/ht/detail/")

    @patch("config.middleware.slow_api.slow_api_alert_triggered.send")
    @override_settings(
        SLOW_API_ALERT_AT_MS=30000, SLOW_API_ALERT_NAMESPACES=["healthcheck_detail"]
    )
    def test_signal_not_triggered_when_get_healthcheck_detail_took_expected_time_to_response(
        self, mock_signal_send
    ):
        self.get_healthcheck_detail()

        self.assertResponseSuccess()
        self.assertFalse(mock_signal_send.called)

    @patch("config.middleware.slow_api.slow_api_alert_triggered.send")
    @override_settings(
        SLOW_API_ALERT_AT_MS=1, SLOW_API_ALERT_NAMESPACES=["healthcheck_detail"]
    )
    def test_signal_triggered_when_get_healthcheck_detail_took_too_much_time_to_response(
        self, mock_signal_send
    ):
        self.get_healthcheck_detail()

        self.assertResponseSuccess()
        self.assertTrue(mock_signal_send.called)

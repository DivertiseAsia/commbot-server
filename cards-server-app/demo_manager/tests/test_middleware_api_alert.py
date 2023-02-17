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


class BaseMiddlewareTestCase(BaseTestCase):

    def assertLogMessageContain(self, contain, output_logs):
        self.assertTrue(any([contain in output for output in output_logs]))


class TestFailedAPIAlertTriggered(BaseMiddlewareTestCase):

    @staticmethod
    def get_mockup_register_payload():
        return {
            "email": "test_middleware_user@divertise.asia",
            "password": "@somerandomPassword",
            "confirm_password": "@somerandomPassword",
            "profile": {
                "first_name": "test_middleware_user",
                "last_name": "divertise",
            }
        }

    def test_logger_does_not_log_when_register_success_w_201_status_code(self):
        self.given_url(reverse("v1:auth-register"))

        with self.assertNoLogs('root', level='WARNING'):
            self.when_user_posts(self.get_mockup_register_payload())

        self.assertResponseCreated()
        print(">> test_logger_does_not_log_when_register_success_w_201_status_code: OK <<")

    def test_logger_does_log_when_register_failed_w_400_status_code_there_no_password_in_payload(self):
        self.given_url(reverse("v1:auth-register"))

        payload = self.get_mockup_register_payload()
        _password = payload.pop("password")

        with self.assertLogs('root', level='WARNING') as cm:
            self.when_user_posts(payload)

        self.assertResponseBadRequest()
        self.assertLogMessageContain("Failed API detected", output_logs=cm.output)
        print(">> test_logger_does_log_when_register_failed_w_400_status_code_there_no_password_in_payload: OK <<")

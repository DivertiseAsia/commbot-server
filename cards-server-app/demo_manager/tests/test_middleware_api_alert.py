# """
# Demo Manager's Slow API Alert
# """
from config.helpers import BaseTestCase
from django.contrib.auth import get_user_model
from django.core import mail
from django.test import override_settings
from rest_framework.reverse import reverse

User = get_user_model()


class BaseMiddlewareTestCase(BaseTestCase):
    def assertLogMessageContain(self, contain, output_logs):
        self.assertTrue(any([contain in output for output in output_logs]))


class TestSlowApiAlertTriggered(BaseMiddlewareTestCase):
    def setUp(self):
        super().setUp()
        self.staff_user = User.objects.create(
            email="staffuser@mockup.test", is_superuser=True
        )

    def get_book_list_first_page(self):
        self.given_url(reverse(f"demo:books-list"))
        self.given_query_params({"page": 1})

        self.when_user_gets_json()

    @override_settings(SLOW_API_ALERT_AT_MS=30000)
    def test_alert_email_not_sent_when_get_book_list_with_valid_page_time_to_response_as_expected(
        self,
    ):
        self.get_book_list_first_page()

        self.assertResponseSuccess()
        self.assertEqual(len(mail.outbox), 0)

    @override_settings(SLOW_API_ALERT_AT_MS=0.001)
    def test_alert_email_sent_when_get_book_list_with_valid_page_took_time_to_response_more_than_expected(
        self,
    ):
        self.get_book_list_first_page()

        self.assertResponseSuccess()
        self.assertEqual(len(mail.outbox), 1)
        alert_email = mail.outbox[0]
        self.assertEqual(alert_email.subject, "[Alert] Slow API detected")
        self.assertIn(self.staff_user.email, alert_email.to)

    @override_settings(SLOW_API_ALERT_AT_MS=30000)
    def test_logger_does_not_log_when_get_book_list_with_valid_page_time_to_response_as_expected(
        self,
    ):
        with self.assertNoLogs("root", level="WARNING"):
            self.get_book_list_first_page()

        self.assertResponseSuccess()

    @override_settings(SLOW_API_ALERT_AT_MS=0.001)
    def test_logger_does_log_when_get_book_list_with_valid_page_took_time_to_response_more_than_expected(
        self,
    ):
        with self.assertLogs("root", level="WARNING") as cm:
            self.get_book_list_first_page()

        self.assertLogMessageContain("Slow API detected", output_logs=cm.output)
        self.assertResponseSuccess()


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
            },
        }

    def test_logger_does_not_log_when_register_success_w_201_status_code(self):
        self.given_url(reverse("v1:auth-register"))

        with self.assertNoLogs("root", level="WARNING"):
            self.when_user_posts(self.get_mockup_register_payload())

        self.assertResponseCreated()

    def test_logger_does_log_when_register_failed_w_400_status_code_there_no_password_in_payload(
        self,
    ):
        self.given_url(reverse("v1:auth-register"))

        payload = self.get_mockup_register_payload()
        _password = payload.pop("password")

        with self.assertLogs("root", level="WARNING") as cm:
            self.when_user_posts(payload)

        self.assertResponseBadRequest()
        self.assertLogMessageContain("Failed API detected", output_logs=cm.output)

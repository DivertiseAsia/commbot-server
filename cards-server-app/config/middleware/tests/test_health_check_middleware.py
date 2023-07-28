# """
# Health Check Middleware
# Ignoring ALLOWED_HOSTS
# """

from config.helpers import BaseTestCase
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import DisallowedHost
from django.test import modify_settings, override_settings

User = get_user_model()

BASE_MIDDLEWARE = settings.MIDDLEWARE


class TestHealthCheckMiddleware(BaseTestCase):
    def request_health_check(self):
        self.response = self.client.get("/ht/")

    def assertHealthCheckPass(self):
        self.assertResponseSuccess()
        self.assertEqual(self.response.content, b"OK")

    @override_settings(ALLOWED_HOSTS=["*"])
    def test_health_check_pass_when_allowed_all_hosts_in_settings(
        self,
    ):
        self.request_health_check()

        self.assertHealthCheckPass()

    @override_settings(ALLOWED_HOSTS=[])
    def test_health_check_pass_when_does_not_allowed_all_hosts_in_settings(
        self,
    ):
        self.request_health_check()

        self.assertHealthCheckPass()

    @modify_settings(
        MIDDLEWARE={"remove": ["config.middleware.healthcheck.HealthCheckMiddleware"]}
    )
    @override_settings(ALLOWED_HOSTS=[])
    def test_health_check_failed_and_raises_disallowed_host_when_does_not_allowed_all_hosts_and_no_health_check_middleware_in_settings(
        self,
    ):
        self.request_health_check()
        self.assertResponseBadRequest()
        self.assertRaises(DisallowedHost)

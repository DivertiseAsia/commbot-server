from django.conf import settings
from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.core.files import File
from django.shortcuts import resolve_url
from django.template.defaultfilters import filesizeformat
from django.utils.html import format_html
from django.utils.http import urlencode
from django.utils.safestring import SafeText
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.test import APITestCase

from user_manager.models import User, Profile


def model_admin_url(obj, name: str = None) -> str:
    """
    Creates a URL to the model admin of a particular object

    via: https://stackoverflow.com/questions/6418592/django-admin-linking-to-related-objects
    """
    url = resolve_url(admin_urlname(obj._meta, SafeText("change")), obj.pk)
    return format_html('<a href="{}">{}</a>', url, name or str(obj))


def get_all_field_names(model_class):
    return [field.name for field in model_class._meta.get_fields()]


def get_no_reply_email():
    return getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@divertise.asia")


class BaseTestCase(APITestCase):
    def setUp(self):
        self.current_user = None
        self.url = None
        self.query_params = None
        self.response = None
        self.response_json = None

    def given_query_params(self, query_params):
        self.query_params = query_params

    def given_url(self, url):
        self.url = url

    def given_a_new_user(
        self, email="someemail@divertise.asia", password="irrelevant", role=None
    ):
        return User.objects.create_user(email, password=password, role=role)

    def given_a_profile_for_user(self, user, first_name="Test", last_name="Smith"):
        return Profile.objects.create(
            user=user, first_name=first_name, last_name=last_name
        )

    def given_logged_in_as_user(self, user):
        self.current_user = user
        self.client.force_login(user)

    def when_user_gets_json(self):
        self.response = self.client.get(self.url, self.query_params, format="json")
        self.response_json = self.response.json()
        return self.response_json

    def when_user_puts_and_gets_json(self, data):
        if self.query_params is not None:
            r = {
                "QUERY_STRING": urlencode(self.query_params, doseq=True),
            }
            self.response = self.client.put(self.url, data, format="json", **r)
        else:
            self.response = self.client.put(self.url, data, format="json")
        self.response_json = self.response.json()
        return self.response_json

    def when_user_posts(self, data):
        if self.query_params is not None:
            r = {
                "QUERY_STRING": urlencode(self.query_params, doseq=True),
            }
            self.response = self.client.post(self.url, data, format="json", **r)
        else:
            self.response = self.client.post(self.url, data, format="json")

    def when_user_posts_and_gets_json(self, data):
        self.when_user_posts(data)
        self.response_json = self.response.json()
        return self.response_json

    def when_user_deletes(self):
        if self.query_params is not None:
            r = {
                "QUERY_STRING": urlencode(self.query_params, doseq=True),
            }
            self.response = self.client.delete(self.url, format="json", **r)
        else:
            self.response = self.client.delete(self.url, format="json")

    def assertResponseSuccess(self):
        self.assertEqual(self.response.status_code, status.HTTP_200_OK)

    def assertResponseCreated(self):
        """
        The response is 201 Created
        """
        self.assertEqual(self.response.status_code, status.HTTP_201_CREATED)

    def assertResponseDeleteSuccess(self):
        self.assertEqual(self.response.status_code, status.HTTP_204_NO_CONTENT)

    def assertResponseBadRequest(self):
        self.assertEqual(self.response.status_code, status.HTTP_400_BAD_REQUEST)

    def assertResponseNotAuthorized(self):
        """
        The response is 401 Unauthorized
        """
        self.assertEqual(self.response.status_code, status.HTTP_401_UNAUTHORIZED)

    def assertResponseForbidden(self):
        """
        The response is 403 Forbidden
        """
        self.assertEqual(self.response.status_code, status.HTTP_403_FORBIDDEN)

    def assertResponseNotFound(self):
        self.assertEqual(self.response.status_code, status.HTTP_404_NOT_FOUND)

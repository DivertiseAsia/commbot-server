# """
# User Manager's Porfile Views
# """
from config.helpers import BaseTestCase
from rest_framework.reverse import reverse
from user_manager.models import Profile, User


class TestProfileViews(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.user_email = "test@divertise.asia"
        self.first_name = "Theo"
        self.last_name = "Burns"

    def test_get_profile_for_logged_out_user_is_not_authorized(self):
        self.given_url(reverse("v1:profile-me"))

        self.when_user_gets_json()
        self.assertResponseNotAuthorized()

    def test_get_profile_for_logged_in_user_with_profile_returns_profile(self):
        user = self.given_a_new_user(email=self.user_email)
        self.given_logged_in_as_user(user)
        self.given_a_profile_for_user(
            user=user, first_name=self.first_name, last_name=self.last_name
        )
        self.given_url(reverse("v1:profile-me"))

        self.when_user_gets_json()

        self.assertResponseSuccess()
        self.assertIn("first_name", self.response_json)
        self.assertIn("last_name", self.response_json)
        self.assertIn("email", self.response_json)
        self.assertEquals(self.first_name, self.response_json["first_name"])
        self.assertEquals(self.last_name, self.response_json["last_name"])
        self.assertEquals(self.user_email, self.response_json["email"])

    def test_get_profile_for_logged_in_user_without_profile_returns_empty_profile_except_email(
        self,
    ):
        user = self.given_a_new_user(email=self.user_email)
        self.given_logged_in_as_user(user)
        self.given_url(reverse("v1:profile-me"))

        self.when_user_gets_json()

        self.assertResponseSuccess()
        self.assertIn("first_name", self.response_json)
        self.assertIn("last_name", self.response_json)
        self.assertIn("email", self.response_json)
        self.assertEquals("", self.response_json["first_name"])
        self.assertEquals("", self.response_json["last_name"])
        self.assertEquals(self.user_email, self.response_json["email"])
        self.assertFalse(Profile.objects.filter(user=user).exists())

    def test_update_profile_with_valid_data_is_okay(self):
        user = self.given_a_new_user(email=self.user_email)
        self.given_a_profile_for_user(
            user=user, first_name=self.first_name, last_name=self.last_name
        )
        self.given_logged_in_as_user(user)
        self.given_url(reverse("v1:profile-me"))

        new_first_name = self.first_name + "a"
        new_last_name = "cat"
        new_email = self.user_email + ".new"
        self.when_user_puts_and_gets_json(
            {
                "email": new_email,
                "first_name": new_first_name,
                "last_name": new_last_name,
            }
        )

        self.assertResponseSuccess()
        self.assertIn("first_name", self.response_json)
        self.assertIn("last_name", self.response_json)
        self.assertIn("email", self.response_json)
        self.assertEquals(new_first_name, self.response_json["first_name"])
        self.assertEquals(new_last_name, self.response_json["last_name"])
        self.assertEquals(new_email, self.response_json["email"])

        profile = Profile.objects.get(user=user)
        self.assertEquals(new_first_name, profile.first_name)
        self.assertEquals(new_last_name, profile.last_name)

        self.assertTrue(User.objects.filter(email=new_email).exists())
        self.assertFalse(User.objects.filter(email=self.user_email).exists())

    def test_update_profile_with_blank_email_is_bad_request(self):
        user = self.given_a_new_user(email=self.user_email)
        self.given_a_profile_for_user(
            user=user, first_name=self.first_name, last_name=self.last_name
        )
        self.given_logged_in_as_user(user)
        self.given_url(reverse("v1:profile-me"))

        new_email = ""
        self.when_user_puts_and_gets_json(
            {
                "email": new_email,
                "first_name": self.first_name,
                "last_name": self.last_name,
            }
        )

        self.assertResponseBadRequest()
        self.assertIn("email", self.response_json)
        self.assertEquals(["This field may not be blank."], self.response_json["email"])

        self.assertTrue(User.objects.filter(email=self.user_email).exists())

    def test_update_creates_profile_and_edits_email_with_valid_data_if_none_is_okay(
        self,
    ):
        user = self.given_a_new_user(email=self.user_email)
        self.given_logged_in_as_user(user)
        self.given_url(reverse("v1:profile-me"))

        new_first_name = self.first_name + "a"
        new_last_name = "cat"
        new_email = self.user_email + ".new"
        self.when_user_puts_and_gets_json(
            {
                "email": new_email,
                "first_name": new_first_name,
                "last_name": new_last_name,
            }
        )

        self.assertResponseSuccess()
        self.assertIn("first_name", self.response_json)
        self.assertIn("last_name", self.response_json)
        self.assertIn("email", self.response_json)
        self.assertEquals(new_first_name, self.response_json["first_name"])
        self.assertEquals(new_last_name, self.response_json["last_name"])
        self.assertEquals(new_email, self.response_json["email"])

        profile = Profile.objects.get(user=user)
        self.assertEquals(new_first_name, profile.first_name)
        self.assertEquals(new_last_name, profile.last_name)

        self.assertTrue(User.objects.filter(email=new_email).exists())
        self.assertFalse(User.objects.filter(email=self.user_email).exists())

    def test_update_creates_profile_without_email_change_with_valid_data_if_none_is_okay(
        self,
    ):
        user = self.given_a_new_user(email=self.user_email)
        self.given_logged_in_as_user(user)
        self.given_url(reverse("v1:profile-me"))

        new_first_name = self.first_name + "a"
        new_last_name = "cat"
        self.when_user_puts_and_gets_json(
            {
                "email": self.user_email,
                "first_name": new_first_name,
                "last_name": new_last_name,
            }
        )

        self.assertResponseSuccess()
        self.assertIn("first_name", self.response_json)
        self.assertIn("last_name", self.response_json)
        self.assertIn("email", self.response_json)
        self.assertEquals(new_first_name, self.response_json["first_name"])
        self.assertEquals(new_last_name, self.response_json["last_name"])
        self.assertEquals(self.user_email, self.response_json["email"])

        profile = Profile.objects.get(user=user)
        self.assertEquals(new_first_name, profile.first_name)
        self.assertEquals(new_last_name, profile.last_name)

        self.assertTrue(User.objects.filter(email=self.user_email).exists())

    def test_update_profile_with_reused_email_is_badrequest(self):
        new_email = self.user_email + ".new"
        user = self.given_a_new_user(email=self.user_email)
        other_user = self.given_a_new_user(email=new_email)
        self.given_a_profile_for_user(
            user=user, first_name=self.first_name, last_name=self.last_name
        )
        self.given_logged_in_as_user(user)
        self.given_url(reverse("v1:profile-me"))

        self.when_user_puts_and_gets_json(
            {
                "email": new_email,
                "first_name": self.first_name,
                "last_name": self.last_name,
            }
        )

        self.assertResponseBadRequest()
        self.assertIn("non_field_errors", self.response_json)
        self.assertEquals(
            ["This email is already being used for another account."],
            self.response_json["non_field_errors"],
        )

    def test_create_profile_with_reused_email_is_badrequest(self):
        reused_email = self.user_email + ".new"
        user = self.given_a_new_user(email=self.user_email)
        other_user = self.given_a_new_user(email=reused_email)
        self.given_logged_in_as_user(user)
        self.given_url(reverse("v1:profile-me"))

        self.when_user_puts_and_gets_json(
            {
                "email": reused_email,
                "first_name": self.first_name,
                "last_name": self.last_name,
            }
        )

        self.assertResponseBadRequest()
        self.assertIn("non_field_errors", self.response_json)
        self.assertEquals(
            ["This email is already being used for another account."],
            self.response_json["non_field_errors"],
        )
        self.assertFalse(Profile.objects.filter(user=user).exists())

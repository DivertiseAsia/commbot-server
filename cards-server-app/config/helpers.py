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

from fractions import Fraction
from pathlib import Path
from PIL import Image
from io import BytesIO

from pictures.models import PictureField, PictureFieldFile
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


image_types = {
    "jpg": "JPEG",
    "jpeg": "JPEG",
    "png": "PNG",
    "gif": "GIF",
    "tif": "TIFF",
    "tiff": "TIFF",
}


def image_resize(image, width, aspect_ratio, quality):
    file_object = None
    with Image.open(image) as img:
        # Convert aspect ratio (type Str) to fraction/None.
        aspect_ratio_num = Fraction(aspect_ratio) if aspect_ratio else None
        # Calculate current aspect ratio as a number
        if not aspect_ratio_num:
            aspect_ratio_num = img.width / img.height
        # Calculate new height
        height = width / aspect_ratio_num
        # Determine if width or height is limiter of image resizing
        if img.width > width or img.height > height:
            output_size = (width, int(height))
            img = img.resize(output_size, Image.ANTIALIAS)
            img_filename = Path(image.file.name).name

            # Save as current format
            img_suffix = Path(image.file.name).name.split(".")[-1]
            img_format = image_types[img_suffix]

            # TODO: test ensure that bytesIO clear out from memory
            # Note: if convert to JPEG need to use .convert("RBGA")
            img_io = BytesIO()
            img.save(img_io, quality=quality, format=img_format, optimize=True)
            file_object = File(img_io)

    return file_object


class CustomImageFieldFile(PictureFieldFile):
    def save(self, name, content, save=True):
        # -------- Resizing image --------
        # Modify original image
        if not self.field.keep_original:
            resized_image = image_resize(
                content,
                self.field.container_width,
                self.field.aspect_ratios[0],
                self.field.quality,
            )

            # -------- Check file sizing --------
            # TODO:
            # try:
            #     if file.size > self.max_upload_size:
            #         print("raise error")
            #         raise forms.ValidationError(
            #             _("Please keep filesize under %s. Current filesize %s")
            #             % (
            #                 filesizeformat(self.max_upload_size),
            #                 filesizeformat(file.size),
            #             )
            #         )
            # except AttributeError:
            #     pass
            super().save(name, resized_image, save)

        # Keep original & Generate new images
        else:
            super().save(name, content, save)
            self.save_all()


# inherit from PictureField (django-pictures)
class CustomImageField(PictureField):
    attr_class = CustomImageFieldFile

    #     * max_upload_size - a number indicating the maximum file size allowed for upload.
    #         2.5MB - 2621440
    #         5MB - 5242880
    #         10MB - 10485760
    #         20MB - 20971520
    #         50MB - 5242880
    #         100MB - 104857600
    #         250MB - 214958080
    #         500MB - 429916160
    #     """

    def __init__(
        self,
        verbose_name=None,
        name=None,
        keep_original=True,
        max_file_size=None,
        quality=75,
        **kwargs,
    ):
        self.max_file_size = max_file_size
        self.keep_original = keep_original
        self.quality = quality
        super().__init__(verbose_name, name, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        return (
            name,
            path,
            args,
            {
                **kwargs,
                "max_file_size": self.max_file_size,
                "keep_original": self.keep_original,
                "quality": self.quality,
            },
        )


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

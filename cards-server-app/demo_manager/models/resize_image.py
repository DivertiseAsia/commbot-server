from django.core.files import File
from django.db import models
from django.db.models import ImageField
from django.forms import forms
from django.template.defaultfilters import filesizeformat
from django.utils.translation import gettext_lazy as _

from pictures import validators
from pictures.models import PictureField
from stdimage.models import StdImageField

from pathlib import Path
from PIL import Image
from io import BytesIO

# image_types = {
#     "jpg": "JPEG",
#     "jpeg": "JPEG",
#     "png": "PNG",
#     "gif": "GIF",
#     "tif": "TIFF",
#     "tiff": "TIFF",
# }


class ExampleImage(models.Model):
    title = models.CharField(max_length=255)
    picture_width = models.PositiveIntegerField(null=True)
    picture_height = models.PositiveIntegerField(null=True)
    picture = PictureField(
        upload_to="pictures",
        aspect_ratios=[None],
        file_types=["JPEG"],
        width_field="picture_width",
        height_field="picture_height",
        blank=True,
        null=True,
    )
    std_image = StdImageField(
        upload_to="path/to/img",
        blank=True,
        null=True,
        variations={
            "large": (600, 400),
        },
        delete_orphans=True,
    )


# class ResizeImageField(ImageField):
#     """
#     * max_width - maximum width of image (based on aspect ratio)
#     * max_height - maximum height of image (based on aspect ratio)
#     * aspect_ratio - width over height (default = 1.0)
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

#     description = "Auto resizing image (keeping aspect ratio) field"

#     def __init__(
#         self, max_width=100, max_height=100, aspect_ratio=1.0, *args, **kwargs
#     ):
#         self.max_width = max_width
#         self.max_height = max_height
#         self.aspect_ratio = aspect_ratio
#         self.max_upload_size = kwargs.pop("max_upload_size", 0)
#         super().__init__(*args, **kwargs)

#     def deconstruct(self):
#         name, path, args, kwargs = super().deconstruct()
#         if self.max_width != 100:
#             kwargs["max_width"] = self.max_width
#         if self.max_height != 100:
#             kwargs["max_height"] = self.max_height
#         if self.aspect_ratio != 1:
#             kwargs["max_height"] = self.aspect_ratio

#         return name, path, args, kwargs

#     # def clean(self, *args, **kwargs):
#     #     data = super(ResizeImageField, self).clean(*args, **kwargs)

#     #     file = data.file
#     #     print("IN CLEAN:", file.size)
#     #     print("MAX UPLOAD SIZE", self.max_upload_size)
#     #     try:
#     #         if file.size > self.max_upload_size:
#     #             print("raise error")
#     #             raise forms.ValidationError(
#     #                 _("Please keep filesize under %s. Current filesize %s")
#     #                 % (
#     #                     filesizeformat(self.max_upload_size),
#     #                     filesizeformat(file.size),
#     #                 )
#     #             )
#     #     except AttributeError:
#     #         pass

#     #     return data


# def image_resize(image, width, height):
#     img = Image.open(image)
#     if img.width > width or img.height > height:
#         output_size = (width, height)
#         img.thumbnail(output_size)
#         img_filename = Path(image.file.name).name
#         img_suffix = Path(image.file.name).name.split(".")[-1]
#         img_format = image_types[img_suffix]
#         buffer = BytesIO()
#         img.save(buffer, format=img_format)
#         file_object = File(buffer)
#         image.save(img_filename, file_object)


# class ExamplePicture(models.Model):
#     _image = ResizeImageField(
#         max_width=100,
#         max_height=100,
#         aspect_ratio=1,
#         max_upload_size=1,
#         blank=True,
#         null=True,
#     )
#     title = models.CharField(_("Title"), max_length=255)

#     # Prevent image from resizing when changing title/other non-image fields
#     def set_image(self, val):
#         self._image = val
#         self._image_changed = True

#     def get_image(self):
#         return self._image

#     image = property(get_image, set_image)

#     @property
#     def image_url(self):
#         if self._image and hasattr(self._image, "url"):
#             return self._image.url

#     def save(self, commit=True, *args, **kwargs):
#         if commit and getattr(self, "_image_changed", True):
#             image_resize(
#                 self._image,
#                 ExamplePicture._meta.get_field("_image").max_width,
#                 ExamplePicture._meta.get_field("_image").max_height,
#             )
#             if (
#                 self._image.size
#                 < ExamplePicture._meta.get_field("_image").max_upload_size
#             ):
#                 super().save(*args, **kwargs)
#             else:
#                 print("LARGER THAN UPLOAD")

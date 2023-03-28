from django.core.files import File
from django.db import models
from django.db.models import ImageField
from django.utils.translation import gettext_lazy as _

from pathlib import Path
from PIL import Image
from io import BytesIO

image_types = {
    "jpg": "JPEG",
    "jpeg": "JPEG",
    "png": "PNG",
    "gif": "GIF",
    "tif": "TIFF",
    "tiff": "TIFF",
}


class ResizeImageField(ImageField):
    description = "Auto resizing image (keepin aspect ratio) field"

    def __init__(self, width=100, height=100, *args, **kwargs):
        self.width = width
        self.height = height
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        if self.width != 100:
            kwargs["width"] = self.width
        if self.height != 100:
            kwargs["height"] = self.height
        return name, path, args, kwargs


def image_resize(image, width, height):
    img = Image.open(image)
    if img.width > width or img.height > height:
        output_size = (width, height)
        img.thumbnail(output_size)
        img_filename = Path(image.file.name).name
        img_suffix = Path(image.file.name).name.split(".")[-1]
        img_format = image_types[img_suffix]
        buffer = BytesIO()
        img.save(buffer, format=img_format)
        file_object = File(buffer)
        image.save(img_filename, file_object)


class ExamplePicture(models.Model):
    image = ResizeImageField(width=100, height=100, blank=True, null=True)
    title = models.CharField(_("Title"), max_length=255)

    def save(self, commit=True, *args, **kwargs):
        if commit:
            image_resize(self.image, self.image.width, self.image.height)
            super().save(*args, **kwargs)


# TODO: https://blog.soards.me/posts/resize-image-on-save-in-django-before-sending-to-amazon-s3/

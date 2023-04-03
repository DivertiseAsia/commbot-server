from fractions import Fraction
from django.core.files import File
from django.db import models
from django.db.models import ImageField
from django.forms import forms
from django.template.defaultfilters import filesizeformat
from django.utils.translation import gettext_lazy as _

from pictures.models import PictureField, PictureFieldFile

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


class ExampleImage(models.Model):
    title = models.CharField(max_length=255)
    picture_width = models.PositiveIntegerField(null=True, blank=True)
    picture_height = models.PositiveIntegerField(null=True, blank=True)
    picture = CustomImageField(
        upload_to="pictures",
        aspect_ratios=[None],
        file_types=["WEBP"],
        container_width=1200,
        width_field="picture_width",
        height_field="picture_height",
        quality=20,
        keep_original=False,
        grid_columns=1,
        pixel_densities=[1],
        blank=True,
        null=True,
    )

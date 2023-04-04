from config.helpers import CustomImageField
from django.db import models


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

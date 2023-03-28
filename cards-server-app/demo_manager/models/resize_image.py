from django.core.files import File
from django.db.models import ImageField

# from pathlib import Path
# from PIL import Image
# from io import BytesIO


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


# def image_resize(image, width, height):
#     # Open the image using Pillow
#     img = Image.open(image)
#     # check if either the width or height is greater than the max
#     if img.width > width or img.height > height:
#         output_size = (width, height)
#         # Create a new resized “thumbnail” version of the image with Pillow
#         img.thumbnail(output_size)
#         # Find the file name of the image
#         img_filename = Path(image.file.name).name
#         # Spilt the filename on “.” to get the file extension only
#         img_suffix = Path(image.file.name).name.split(".")[-1]
#         # Use the file extension to determine the file type from the image_types dictionary
#         img_format = image_types[img_suffix]
#         # Save the resized image into the buffer, noting the correct file type
#         buffer = BytesIO()
#         img.save(buffer, format=img_format)
#         # Wrap the buffer in File object
#         file_object = File(buffer)
#         # Save the new resized file as usual, which will save to S3 using django-storages
#         image.save(img_filename, file_object)

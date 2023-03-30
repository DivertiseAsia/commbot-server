from import_export.admin import ImportExportModelAdmin

from ..models import ExampleImage


# class ExamplePictureAdminView(ImportExportModelAdmin):
#     model = ExamplePicture
#     search_fields = ("title",)
#     readonly_fields = ("image_url",)


class ExampleImageAdminView(ImportExportModelAdmin):
    model = ExampleImage
    search_fields = ("title",)

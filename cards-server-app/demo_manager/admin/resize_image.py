from import_export.admin import ImportExportModelAdmin

from ..models import ExampleImage


class ExampleImageAdminView(ImportExportModelAdmin):
    model = ExampleImage
    search_fields = ("title",)

from import_export.admin import ImportExportModelAdmin

from demo_manager.models import ExampleImage


class ExampleImageAdminView(ImportExportModelAdmin):
    model = ExampleImage
    search_fields = ("title",)

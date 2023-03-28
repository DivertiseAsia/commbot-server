from import_export.admin import ImportExportModelAdmin

from ..models import ExamplePicture


class ExamplePictureAdminView(ImportExportModelAdmin):
    model = ExamplePicture

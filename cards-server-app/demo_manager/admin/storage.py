from import_export.admin import ImportExportModelAdmin

from ..models import UserBookStorage


class UserBookStorageAdminView(ImportExportModelAdmin):
    model = UserBookStorage

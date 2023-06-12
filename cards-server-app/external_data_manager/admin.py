from django.contrib import admin

from import_export.admin import ImportExportModelAdmin

from external_data_manager.models import MtgCard


class MtgCardAdminView(ImportExportModelAdmin):
    model = MtgCard
    list_display = (
        "name",
        "search_text",
        "type_line",
        "last_updated",
        "external_id",
    )

    search_fields = ("id", "name", "search_text", "external_id")


admin.site.register(MtgCard, MtgCardAdminView)

admin.site.site_header = "External Data Administration"
admin.site.site_title = "External Data Admin"

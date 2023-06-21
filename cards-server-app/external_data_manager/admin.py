from django.contrib import admin

from import_export.admin import ImportExportModelAdmin

from external_data_manager.models import MtgCard
from .helpers import update_query_from_scryfall


class MtgCardAdminView(ImportExportModelAdmin):
    actions = ["refresh_data"]
    model = MtgCard
    list_display = (
        "name",
        "search_text",
        "type_line",
        "last_updated",
        "external_id",
    )

    search_fields = ("id", "name", "search_text", "external_id")

    def refresh_data(self, request, queryset):
        for obj in queryset:
            update_query_from_scryfall(obj.search_text)


admin.site.register(MtgCard, MtgCardAdminView)

admin.site.site_header = "External Data Administration"
admin.site.site_title = "External Data Admin"

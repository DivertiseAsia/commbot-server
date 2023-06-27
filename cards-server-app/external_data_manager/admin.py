from django.contrib import admin

from import_export.admin import ImportExportModelAdmin

from external_data_manager.models import (
    MtgCard,
    MtgStorePrice,
    MtgStore,
    AdditionalStep,
)
from .helpers import update_query_from_scryfall


class MtgCardPriceInline(admin.TabularInline):
    model = MtgStorePrice
    extra = 0


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
    inlines = (MtgCardPriceInline,)

    search_fields = ("id", "name", "search_text", "external_id")

    def refresh_data(self, request, queryset):
        for obj in queryset:
            update_query_from_scryfall(obj.search_text)


class AdditionalStepInline(admin.TabularInline):
    model = AdditionalStep
    extra = 1


class MtgStoreAdminView(ImportExportModelAdmin):
    model = MtgStore
    list_display = ("name",)
    inlines = (AdditionalStepInline,)


admin.site.register(MtgCard, MtgCardAdminView)
admin.site.register(MtgStore, MtgStoreAdminView)

admin.site.site_header = "External Data Administration"
admin.site.site_title = "External Data Admin"

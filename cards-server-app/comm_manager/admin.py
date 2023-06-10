from django.contrib import admin

from import_export.admin import ImportExportModelAdmin

from comm_manager.models import Chat


class ChatAdminView(ImportExportModelAdmin):
    model = Chat
    list_display = ("id", "chat_type", "joined_date", "ended_date", "external_id")

    search_fields = ("id", "external_id")


admin.site.register(Chat, ChatAdminView)

admin.site.site_header = "Communication Administration"
admin.site.site_title = "Communication Admin"

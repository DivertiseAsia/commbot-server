from django.contrib import admin

from import_export.admin import ImportExportModelAdmin

from comm_manager.models import Chat, ChatUser, ChatMembership

from comm_manager.tasks import get_profile_for_user


class ChatMembershipInlineAdmin(admin.TabularInline):
    model = ChatMembership
    extra = 0


class ChatUserAdminView(ImportExportModelAdmin):
    model = ChatUser
    list_display = ("id", "external_id", "display_name", "last_pulled_date")

    search_fields = ("id", "external_id", "display_name")
    inlines = (ChatMembershipInlineAdmin,)
    actions = ["pull_user_data"]

    def pull_user_data(self, request, queryset):
        for obj in queryset:
            get_profile_for_user.delay(obj.external_id)

        self.message_user(
            request,
            "Pulling user data for selected users",
        )


class ChatAdminView(ImportExportModelAdmin):
    model = Chat
    list_display = ("id", "chat_type", "joined_date", "ended_date", "external_id")

    search_fields = ("id", "external_id")


admin.site.register(ChatUser, ChatUserAdminView)
admin.site.register(Chat, ChatAdminView)

admin.site.site_header = "Communication Administration"
admin.site.site_title = "Communication Admin"

from django.conf import settings
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.template.response import TemplateResponse
from django.urls import path

from import_export.admin import ImportMixin, ImportExportModelAdmin
from import_export import resources

from user_manager.forms import (
    UserAdminCreationForm,
    UserAdminChangeForm,
)
from user_manager.models import User, Profile

from config.helpers import model_admin_url


class UserAdminView(ImportMixin, BaseUserAdmin):
    form = UserAdminChangeForm
    add_form = UserAdminCreationForm

    list_display = ("email", "is_superuser", "is_active", "last_login")
    list_filter = ("is_superuser", "is_active")
    readonly_fields = (
        "id",
        "is_superuser",
    )
    fieldsets = (
        (None, {"fields": ("id", "email", "password")}),
        ("Permissions", {"fields": ("groups",)}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "password1",
                    "password2",
                ),
            },
        ),
    )
    search_fields = ("email",)
    ordering = ("email",)
    filter_horizontal = ()

    def get_urls(self):
        urls = super().get_urls()
        if settings.DEBUG:
            my_urls = [
                path("social_login_test", self.social_login_test),
            ]
            return my_urls + urls
        else:
            return urls

    def social_login_test(self, request):
        # used to test and show social login from server
        # should be something like /admin/user_manager/user/social_login_test
        return TemplateResponse(
            request,
            "admin/social_login_test.html",
            {},
        )


class ProfileResource(resources.ModelResource):
    class Meta:
        model = Profile
        use_natural_foreign_keys = True


class ProfileAdminView(ImportExportModelAdmin):
    model = Profile
    list_display = ("__str__", "user_link", "first_name", "last_name")

    search_fields = ("user__email", "first_name", "last_name")
    autocomplete_fields = ["user"]

    resource_classes = [ProfileResource]

    def user_link(self, obj):
        return model_admin_url(obj.user)


admin.site.register(User, UserAdminView)
admin.site.register(Profile, ProfileAdminView)

admin.site.site_header = "User Administration"
admin.site.site_title = "User Admin"

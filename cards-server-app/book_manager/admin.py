from django.contrib import admin

from config.helpers import get_all_field_names

from .models import Author, Book


class AuthorAdminView(admin.ModelAdmin):
    model = Author
    list_display = ("name", )
    search_fields = ("name", )


class BookAdminView(admin.ModelAdmin):
    model = Book
    fields = get_all_field_names(Book)
    readonly_fields = ("id", "created_at", )
    list_display = ("id", "title", "author_names", )
    search_fields = ("id", "title", "author_names", )
    autocomplete_fields = ["authors"]


admin.site.register(Author, AuthorAdminView)
admin.site.register(Book, BookAdminView)

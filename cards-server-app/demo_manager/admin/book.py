from django.contrib.admin.views.main import ChangeList
from django.contrib.postgres.aggregates import StringAgg

from config.helpers import get_all_field_names
from import_export.admin import ImportExportModelAdmin


from ..models import Author, Book, BookWithIndex


class AuthorAdminView(ImportExportModelAdmin):
    model = Author
    list_display = ("name", )
    search_fields = ("name", )


class BookChangeList(ChangeList):
    """
    BookChangeList
    ---
    Annotates book author names in `get_queryset` function to display in list_display without several hit database
    """

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            author_names=StringAgg("authors__name", delimiter=", ", ordering="authors__name"),
        )
        return queryset


class BookAdminView(ImportExportModelAdmin):
    model = Book
    fields = get_all_field_names(Book)
    readonly_fields = ("id", "created_at", )
    list_display = ("id", "title", "author_names", )
    search_fields = ("id", "title", "authors", )
    autocomplete_fields = ["authors"]

    def get_changelist(self, request, **kwargs):
        return BookChangeList

    def author_names(self, book):
        return book.author_names


class BookWithIndexAdminView(BookAdminView):
    model = BookWithIndex
    fields = get_all_field_names(BookWithIndex)

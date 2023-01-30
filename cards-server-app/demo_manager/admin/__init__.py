from django.contrib import admin

from .book import BookAdminView, AuthorAdminView, Book, Author


admin.site.register(Author, AuthorAdminView)
admin.site.register(Book, BookAdminView)


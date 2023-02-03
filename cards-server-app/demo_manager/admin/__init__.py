from django.contrib import admin

from .book import Author, AuthorAdminView, Book, BookAdminView, BookWithIndex, BookWithIndexAdminView


admin.site.register(Author, AuthorAdminView)
admin.site.register(Book, BookAdminView)
admin.site.register(BookWithIndex, BookWithIndexAdminView)

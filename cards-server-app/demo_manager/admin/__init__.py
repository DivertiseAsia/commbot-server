from django.contrib import admin

from .book import (
    Author,
    AuthorAdminView,
    Book,
    BookAdminView,
    BookWithIndex,
    BookWithIndexAdminView,
)
from .storage import UserBookStorageAdminView, UserBookStorage
from .resize_image import ExamplePictureAdminView, ExamplePicture

admin.site.register(Author, AuthorAdminView)
admin.site.register(Book, BookAdminView)
admin.site.register(BookWithIndex, BookWithIndexAdminView)
admin.site.register(UserBookStorage, UserBookStorageAdminView)
admin.site.register(ExamplePicture, ExamplePictureAdminView)

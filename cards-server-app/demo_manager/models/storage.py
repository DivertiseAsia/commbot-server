from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _
from user_manager.models import Profile

from .book import BookWithIndex

User = get_user_model()


class UserBookStorage(models.Model):
    owner = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name="book_storage")
    books = models.ManyToManyField(BookWithIndex, blank=True)

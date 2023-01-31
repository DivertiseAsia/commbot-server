import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _


class Author(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name = _("author")
        verbose_name_plural = _("authors")

    def __str__(self):
        return f"{self.name}"


class Book(models.Model):
    id = models.UUIDField(_("ID"), primary_key=True, default=uuid.uuid4, editable=False)
    isbn = models.CharField(_("ISBN: The International Standard Book Number"), max_length=255, unique=True)
    title = models.CharField(_("Title"), max_length=255)
    authors = models.ManyToManyField(Author, blank=False, related_name="books")
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)

    class Meta:
        verbose_name = _("book")
        verbose_name_plural = _("books")
        ordering = ["title"]

    @property
    def author_names(self):
        return ", ".join(list(self.authors.all().values_list('name', flat=True)))

    def __str__(self):
        return f"{self.title} - {self.author_names}"

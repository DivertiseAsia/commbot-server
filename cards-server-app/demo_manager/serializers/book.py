from rest_framework import serializers

from ..models import Book


class BookSerializer(serializers.ModelSerializer):
    authors = serializers.SlugRelatedField(many=True, read_only=True, slug_field="name")

    class Meta:
        model = Book
        fields = ("id", "isbn", "title", "authors", "created_at")

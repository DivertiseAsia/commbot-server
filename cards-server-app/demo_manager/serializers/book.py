from rest_framework import serializers

from ..models import Book, BookWithIndex


class BookSerializer(serializers.ModelSerializer):
    authors = serializers.SlugRelatedField(many=True, read_only=True, slug_field="name")

    class Meta:
        model = Book
        fields = ("id", "isbn", "title", "authors", "created_at")


class BookWithIndexSerializer(BookSerializer):
    class Meta:
        model = BookWithIndex
        fields = ("id", "isbn", "title", "authors", "created_at")

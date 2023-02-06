from rest_framework import serializers

from ..models import Book, BookWithIndex


class BookSerializer(serializers.ModelSerializer):
    authors = serializers.SlugRelatedField(many=True, read_only=True, slug_field="name")

    class Meta:
        model = Book
        fields = ("id", "isbn", "title", "authors", "created_at")

    @staticmethod
    def setup_eager_loading(queryset):
        """ Perform necessary eager loading of data. """
        # select_related for "one-to-one" "many-to-one" relationships
        # prefetch_related for "to-many" relationships
        queryset = queryset.prefetch_related('authors')
        return queryset


class BookWithIndexSerializer(BookSerializer):
    class Meta:
        model = BookWithIndex
        fields = ("id", "isbn", "title", "authors", "created_at")


from rest_framework import serializers

from .book import BookWithIndexSerializer
from ..models import UserBookStorage


class UserBookStorageSerializer(serializers.ModelSerializer):
    books = BookWithIndexSerializer(many=True)

    class Meta:
        model = UserBookStorage
        fields = ("owner", "books")

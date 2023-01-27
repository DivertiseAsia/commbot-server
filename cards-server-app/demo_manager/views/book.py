from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from config.mixins import PaginationListViewSetMixin

from ..models import Book
from ..serializers import BookSerializer


class BookViewSetV1(PaginationListViewSetMixin, viewsets.ReadOnlyModelViewSet):
    permission_classes = (AllowAny,)
    serializer_class = BookSerializer
    queryset = Book.objects.all()

    OVERRIDE_PAGE_SIZE = 10

    filterset_fields = {
        "title": ["exact", "icontains", ],
        "authors__name": ["exact", "icontains", ],
    }
    ordering_fields = ["title"]
    search_fields = ["title", "authors__name"]

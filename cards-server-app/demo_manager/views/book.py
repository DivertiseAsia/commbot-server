from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from config.mixins import PaginationWithEagerLoadingViewSetMixin

from ..models import Book, BookWithIndex
from ..serializers import BookSerializer, BookWithIndexSerializer


class BookViewSetV1(PaginationWithEagerLoadingViewSetMixin, viewsets.ReadOnlyModelViewSet):
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


class BookWithIndexViewSetV1(BookViewSetV1):
    serializer_class = BookWithIndexSerializer
    queryset = BookWithIndex.objects.prefetch_related("authors")


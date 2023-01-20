from django.utils.translation import gettext_lazy as _

from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny

from config.mixins import PaginationListViewSetMixin
from .models import Book
from .serializers import BookSerializer


class BookPagination(PageNumberPagination):
    page_size = 10
    max_page_size = 10
    page_size_query_param = "page_size"
    page_query_description = _('A page number within the paginated result set. page "0" would return a list result '
                               'without paginated')


class BookViewSetV1(PaginationListViewSetMixin, viewsets.ReadOnlyModelViewSet):
    permission_classes = (AllowAny, )
    serializer_class = BookSerializer
    pagination_class = BookPagination
    queryset = Book.objects.all()

    filterset_fields = {
            "title": ["exact", "icontains", ],
            "authors__name": ["exact", "icontains", ],
    }
    ordering_fields = ["title"]
    search_fields = ["title", "authors__name"]

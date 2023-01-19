from django.utils.translation import gettext_lazy as _

from rest_framework import viewsets, filters
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny

from .models import Book
from .serializers import BookSerializer


class BookPagination(PageNumberPagination):
    page_size = 10
    max_page_size = 10
    page_size_query_param = "page_size"
    page_query_description = _('A page number within the paginated result set. page "0" would return a list result '
                               'without paginated')


class BookViewSetV1(viewsets.ReadOnlyModelViewSet):
    permission_classes = (AllowAny, )
    serializer_class = BookSerializer
    pagination_class = BookPagination
    queryset = Book.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = ["title", "authors__name"]

    def list(self, request, *args, **kwargs):
        if str(request.query_params.get("page", "")) == "0":
            self.pagination_class = None

        return super().list(request, args, kwargs)

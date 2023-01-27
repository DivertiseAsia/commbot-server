from django_filters.rest_framework import DjangoFilterBackend
from django.utils.translation import gettext_lazy as _

from rest_framework import filters
from rest_framework.pagination import PageNumberPagination


class DefaultPagination(PageNumberPagination):
    page_size = 100
    max_page_size = 100
    page_size_query_param = "page_size"
    page_query_description = _('A page number within the paginated result set. page "-1" would return a list result '
                               'without paginated')


class PaginationListViewSetMixin:
    """
    Pagination List ViewSet Mixin
    ---
    - Using Rest Framework Pagination Class
        - The page number start at 1
        - If page is -1 it would return results list without Pagination
    - Supports search, and django-filter filter backends
        These fields are required to enable filter backend
        - django-filter:
            filterset_fields = {
                <field_name>: Array<queryset_filter_type>,  # (i.e. "exact", "icontains")
            }
        - search:
            search_fields = Array<field_name>
    """
    pagination_class = DefaultPagination

    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]

    def get_paginator_page_query_param(self):
        if not getattr(self, "paginator", None) or not self.paginator:
            raise NotImplementedError(
                "{} is missing Rest Framework the Pagination class.".format(
                    self.__class__.__name__
                )
            )

        return self.paginator.page_query_param

    def get_page_number_in_query_param(self, request) -> str:
        page_key = self.get_paginator_page_query_param()
        return str(request.query_params.get(page_key, ""))

    def list(self, request, *args, **kwargs):
        # Remove pagination_class and _paginator if request page is -1
        if self.get_page_number_in_query_param(request) == "-1":
            self.pagination_class = None
            self._paginator = None

        return super().list(request, args, kwargs)

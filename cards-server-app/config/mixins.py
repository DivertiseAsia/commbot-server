from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import filters


class PaginationListViewSetMixin:
    """
    Pagination List ViewSet Mixin
    ---
    - Using Rest Framework Pagination Class
        If page is 0 it would return results list without Pagination
    - Supports search, and django-filter filter backends
        These fields are required to enable filter backend
        - django-filter:
            filterset_fields = {
                <field_name>: Array<queryset_filter_type>,  # (i.e. "exact", "icontains")
            }
        - serach:
            search_fields = Array<field_name>
    """

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
        """Remove pagination_class and _paginator if request page is 0"""
        if self.get_page_number_in_query_param(request) == "0":
            self.pagination_class = None
            self._paginator = None

        return super().list(request, args, kwargs)

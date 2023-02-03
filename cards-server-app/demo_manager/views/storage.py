from django.contrib.auth import get_user_model
from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from config.mixins import PaginationWithEagerLoadingViewSetMixin

from ..models import BookWithIndex
from ..serializers import BookWithIndexSerializer

User = get_user_model()


class UserBookStorageViewSetV1(PaginationWithEagerLoadingViewSetMixin, viewsets.ReadOnlyModelViewSet):
    permission_classes = (AllowAny,)
    serializer_class = BookWithIndexSerializer
    queryset = BookWithIndex.objects.none()

    OVERRIDE_PAGE_SIZE = 10

    def get_queryset(self):
        self.queryset = self.request.user.book_storage.books
        return super().get_queryset()

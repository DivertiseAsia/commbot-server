from django.contrib.auth import get_user_model
from rest_framework.mixins import ListModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from config.mixins import PaginationWithEagerLoadingViewSetMixin

from ..models import BookWithIndex, UserBookStorage
from ..serializers import BookWithIndexSerializer

User = get_user_model()


class UserBookStorageViewSetV1(PaginationWithEagerLoadingViewSetMixin, ListModelMixin, GenericViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = BookWithIndexSerializer
    queryset = BookWithIndex.objects.none()

    OVERRIDE_PAGE_SIZE = 10

    def get_queryset(self):
        try:
            self.queryset = self.request.user.book_storage.books
        except UserBookStorage.DoesNotExist:
            pass

        return super().get_queryset()

from django.conf.urls.static import static
from django.conf import settings
from django.urls import path, include

from pictures.conf import get_settings
from rest_framework import routers

from demo_manager.views import (
    BookViewSetV1,
    BookWithIndexViewSetV1,
    UserBookStorageViewSetV1,
)


router_demo = routers.DefaultRouter()
router_demo.register(r"books", BookViewSetV1, basename="books")
router_demo.register(r"books_w_index", BookWithIndexViewSetV1, basename="books_w_index")
router_demo.register(r"storage", UserBookStorageViewSetV1, basename="storage")

urlpatterns = [
    path("api/v1/demo/", include((router_demo.urls, "demo-api"), namespace="demo")),
]

if get_settings().USE_PLACEHOLDERS:
    urlpatterns += [
        path("_pictures/", include("pictures.urls")),
    ]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

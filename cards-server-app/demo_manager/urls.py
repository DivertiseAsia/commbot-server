from django.urls import path, include

from rest_framework import routers

from demo_manager.views import BookViewSetV1, BookWithIndexViewSetV1


router_demo = routers.DefaultRouter()
router_demo.register(r"books", BookViewSetV1, basename="books")
router_demo.register(r"books_w_index", BookWithIndexViewSetV1, basename="books_w_index")

urlpatterns = [
        path("api/v1/demo/", include((router_demo.urls, "demo-api"), namespace="demo")),
]

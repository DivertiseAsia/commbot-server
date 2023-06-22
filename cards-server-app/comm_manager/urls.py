from django.urls import path, include

from rest_framework import routers

from .views import (
    CommViewSet,
)


router_comm = routers.DefaultRouter()
router_comm.register(r"", CommViewSet, basename="")

urlpatterns = [
    path(
        "api/v1/comm/",
        include((router_comm.urls, "comm-manager-api"), namespace="comm-manager"),
    ),
]

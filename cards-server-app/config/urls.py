"""cards URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import routers


from demo_manager.views import BookViewSetV1
from user_manager.views import AuthViewSetV1, ProfileViewSetV1


def trigger_error(request):
    oh_no = 1 / 0


api_v1 = get_schema_view(
    openapi.Info(
        title="API",
        default_version="v1",
        description="API for application",
    ),
)

router_v1 = routers.DefaultRouter()
router_v1.register(r"auth", AuthViewSetV1, basename="auth")
router_v1.register(r"profile", ProfileViewSetV1, basename="profile")


router_demo = routers.DefaultRouter()
router_demo.register(r"books", BookViewSetV1, basename="books")

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "api-explorer/",
        api_v1.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("api/v1/", include((router_v1.urls, "api"), namespace="v1")),
    path("accounts/", include("rest_framework.urls", namespace="rest_framework")),
    path(
        "api/v1/social-auth/", include("social_django.urls", namespace="social")
    ),  # for server based login; otherwise can remove
    path(
        "api/v1/social-auth/oauth-login/", include("rest_social_auth.urls_token")
    ),  # for app based login; otherwise can remove
    path(
        "api/v1/auth/reset/",
        include("django_rest_passwordreset.urls", namespace="password_reset"),
    ),
    path("api/v1/demo/", include((router_demo.urls, "demo-api"), namespace="demo")),  # for demo_manager can remove
    path("trigger_error/", trigger_error),
    path("ht/", include("health_check.urls")),
]

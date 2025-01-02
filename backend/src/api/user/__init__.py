from django.urls import path, include
from rest_framework import routers
from .user import UserViewSet

router = routers.DefaultRouter()
router.register(r"user", UserViewSet, basename="user")


urlpatterns = [
    path("", include(router.urls)),
]

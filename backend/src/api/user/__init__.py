from django.urls import path, include
from rest_framework import routers
from .user import UserViewSet
from .token import TokenRefreshView
router = routers.DefaultRouter()
router.register(r"user", UserViewSet, basename="user")


urlpatterns = [
    path("", include(router.urls)),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

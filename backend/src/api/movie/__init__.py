from django.urls import path, include
from rest_framework import routers
from .movie import MovieViewSet

router = routers.DefaultRouter()
router.register(r"movie", MovieViewSet, basename="movie")

urlpatterns = [
    path("", include(router.urls)),
]
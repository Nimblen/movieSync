from django.urls import path, include
from rest_framework import routers
from .movie import MovieUploadView, MovieViewSet

router = routers.DefaultRouter()
router.register(r"movie", MovieViewSet, basename="movie")

urlpatterns = [
    path("", include(router.urls)),
    path('upload/', MovieUploadView.as_view(), name='movie-upload'),
]
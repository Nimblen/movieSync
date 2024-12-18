from django.urls import path, include
from rest_framework import routers
from .movie import MovieFileUploadView, MovieViewSet

router = routers.DefaultRouter()
router.register(r"movie", MovieViewSet, basename="movie")

urlpatterns = [
    path("", include(router.urls)),
    path('upload/', MovieFileUploadView.as_view(), name='upload_movie'),
]
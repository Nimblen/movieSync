from rest_framework.viewsets import ModelViewSet
from rest_framework import generics

from src.apps.movie.models import Movie, MovieFile
from src.apps.movie.serializers.movie import MovieSerializer, MovieFileSerializer


class MovieViewSet(ModelViewSet):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer

class MovieFileUploadView(generics.CreateAPIView):
    queryset = MovieFile.objects.all()
    serializer_class = MovieFileSerializer
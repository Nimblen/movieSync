from rest_framework.viewsets import ModelViewSet

from src.apps.movie.models import Movie
from src.apps.movie.serializers.movie import MovieSerializer


class MovieViewSet(ModelViewSet):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer


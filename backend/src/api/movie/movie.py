from rest_framework.viewsets import ModelViewSet
from rest_framework import generics, status
import os
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser

from src.apps.movie.tasks import process_movie_upload
from src.apps.movie.models import Movie, MovieUpload
from src.apps.movie.serializers.movie import MovieSerializer, MovieUploadSerializer


class MovieViewSet(ModelViewSet):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer

class MovieUploadView(generics.CreateAPIView):
    queryset = MovieUpload.objects.all()
    serializer_class = MovieUploadSerializer
    parser_classes = (MultiPartParser, FormParser)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        movie_upload_obj = serializer.save()
        process_movie_upload.delay(movie_upload_obj.id)
        return Response({
            "detail": "Видео принято и поставлено в очередь на обработку.",
            "upload_id": movie_upload_obj.id,
            "status": movie_upload_obj.status
        }, status=status.HTTP_201_CREATED)

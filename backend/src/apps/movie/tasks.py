from celery import shared_task
from src.apps.movie.services.video_converter import convert_to_hls
from src.apps.movie.models import MovieFile
import os
from django.conf import settings

@shared_task
def convert_movie_task(movie_id):
    movie = MovieFile.objects.get(id=movie_id)
    input_path = movie.video_file.path
    output_dir = os.path.join(settings.MEDIA_ROOT, 'hls', str(movie.id))
    
    try:
        hls_path = convert_to_hls(input_path, output_dir)
        movie.hls_playlist = os.path.relpath(hls_path, settings.MEDIA_ROOT)
        movie.is_converted = True
        movie.save()
    except Exception as e:
        print(f"Error converting movie: {e}")

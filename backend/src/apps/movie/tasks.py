import os
import subprocess
from django.conf import settings
from celery import shared_task
from src.apps.movie.services.video_converter import convert_to_hls
from src.apps.movie.models.movie import Movie, MovieUpload
from src.apps.core.constants import FileUploadStatus
from src.apps.core.utils import is_gpu_available
@shared_task
def process_movie_upload(movie_upload_id):
    '''Function to convert video to HLS and create Movie object'''
    try:
        upload_obj = MovieUpload.objects.get(id=movie_upload_id)
    except MovieUpload.DoesNotExist:
        return f"MovieUpload c id={movie_upload_id} не найден."
    input_file_path = upload_obj.video_file.path
    output_dir = os.path.join(settings.MEDIA_ROOT, 'hls', str(upload_obj.id))
    try:
        hls_path = convert_to_hls(input_file_path, output_dir, base_name="index")
    except subprocess.CalledProcessError as e:
        upload_obj.status = FileUploadStatus.FAILED
        upload_obj.save()
        return f"FFmpeg error: {e}"
    except Exception as e:
        upload_obj.status = FileUploadStatus.FAILED
        upload_obj.save()
        return f"Error: {e}"
    relative_playlist_path = os.path.relpath(hls_path, settings.MEDIA_ROOT)
    hls_playlist_url = f"{settings.MEDIA_URL}{relative_playlist_path}".replace('\\','/')

    movie = Movie.objects.create(
        title=upload_obj.title,
        description=upload_obj.description,
        hls_playlist=hls_playlist_url
    )
    if os.path.exists(input_file_path):
        os.remove(input_file_path)
    upload_obj.status = FileUploadStatus.SUCCESS
    upload_obj.save()

    return f"Создан Movie (id={movie.id}) с HLS={hls_playlist_url}"
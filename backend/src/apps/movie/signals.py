from django.db.models.signals import post_save
from django.dispatch import receiver
from src.apps.movie.models import MovieFile
from src.apps.movie.tasks import convert_movie_task

@receiver(post_save, sender=MovieFile)
def convert_movie_to_hls_async(sender, instance, created, **kwargs):
    if created and not instance.is_converted:
        convert_movie_task.delay(instance.id)

from django.db import models


from src.apps.core.models.abstracts import TimeStampedModel
from src.apps.core.constants import FileUploadStatus


class Category(TimeStampedModel):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Movie(TimeStampedModel):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    hls_playlist = models.URLField(blank=True, null=True)
    categories = models.ManyToManyField(Category, related_name="movies", blank=True)

    def __str__(self):
        return self.title

    def get_first_image(self):
        return self.images.first() if self.images.exists() else None


class MovieUpload(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    video_file = models.FileField(upload_to="temp_videos/")
    status = models.CharField(
        max_length=50,
        choices=FileUploadStatus.FILE_UPLOAD_STATUS_CHOICES,
        default=FileUploadStatus.PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)

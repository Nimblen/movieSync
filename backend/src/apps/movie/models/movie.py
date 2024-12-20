import os
from django.conf import settings
from django.db import models


from src.apps.movie.services.video_converter import convert_to_hls
from src.apps.core.models.abstracts import TimeStampedModel


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
    



class MovieFile(TimeStampedModel):
    title = models.CharField(max_length=255)
    video_file = models.FileField(upload_to='movies/')  
    hls_playlist = models.URLField(blank=True, null=True)
    is_converted = models.BooleanField(default=False)  

    def __str__(self):
        return self.title
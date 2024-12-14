from django.db import models


from src.apps.core.models.abstracts import TimeStampedModel


class Category(TimeStampedModel):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Movie(TimeStampedModel):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    hls_playlist = models.URLField(blank=True, null=True)
    categories = models.ManyToManyField(Category, related_name="movies", blank=True, null=True)

    def __str__(self):
        return self.title



    def get_first_image(self):
        return self.images.first()
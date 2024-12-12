from django.db import models


from src.apps.core.models.abstracts import TimeStampedModel
from src.apps.movie.models.movie import Movie



class MovieImages(TimeStampedModel):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="movie_images/")

    class Meta:
        verbose_name = "Movie Image"
        verbose_name_plural = "Movie Images"

    def __str__(self) -> str:
        return f"{self.movie} - {self.image}"
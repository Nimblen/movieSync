from src.apps.core.utils.rpc_registry import rpc_method
from src.apps.movie.models.movie import Movie


@rpc_method
async def get_movie(params):
    movie = await Movie.objects.prefetch_related("categories").aget(
        id=params["movie_id"]
    )
    categories = [
        {"id": category.id, "name": category.name}
        for category in movie.categories.all()
    ]
    return {
        "id": movie.id,
        "title": movie.title,
        "description": movie.description,
        "hls_playlist": movie.hls_playlist,
        "categories": categories,
    }

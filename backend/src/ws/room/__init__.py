from django.urls import re_path
from src.ws.room.consumers import MovieStateConsumer

movie_websocket_urlpatterns = [
    re_path(r'ws/movie/(?P<room_name>[^/]+)/', MovieStateConsumer.as_asgi()),
]
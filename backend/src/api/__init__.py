from .room import urlpatterns as room_urls
from .movie import urlpatterns as movie_urls
from .user import urlpatterns as user_urls

urlpatterns = movie_urls + room_urls + user_urls
from django.urls import re_path
from .consumers import MainConsumer

websocket_urlpatterns = [
    re_path(r'^ws/app(?:/(?P<room_name>[^/]+))?$', MainConsumer.as_asgi()),
]
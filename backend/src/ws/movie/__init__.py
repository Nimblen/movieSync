from django.urls import path
from src.apps.core.consumers import JSONRPCConsumer

websocket_urlpatterns = [
    path('ws/movie/<str:movie_id>/', JSONRPCConsumer.as_asgi()),
]
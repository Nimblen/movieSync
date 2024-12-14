from django.urls import path, include
from rest_framework import routers
from .room import RoomViewSet

router = routers.DefaultRouter()
router.register(r"room", RoomViewSet, basename="room")


urlpatterns = [
    path("", include(router.urls)),
]

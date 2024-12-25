from rest_framework import serializers
from src.apps.core.constants import RoomTypes
from src.apps.room.validators.room_validator import UniqueRoomValidator
from src.apps.room.services.room_service import RoomService
from src.apps.core.repositories.redis_repository import RedisRepository

repository = RedisRepository()
room_service = RoomService(repository)

class RoomSerializer(serializers.Serializer):
    room_id = serializers.CharField(max_length=255, validators=[UniqueRoomValidator(room_service)])
    movie_id = serializers.CharField(max_length=255)
    room_owner = serializers.CharField(max_length=255)
    room_type = serializers.ChoiceField(choices=RoomTypes.ROOM_TYPE_CHOICES)
    max_users = serializers.IntegerField(default=5, min_value=1)
    room_password = serializers.CharField(max_length=255, required=False)



from rest_framework.exceptions import ValidationError
from src.apps.room.services import RoomManager, RoomUserManager
from src.apps.core.constants import RoomTypes
class UniqueRoomValidator:
    def __init__(self, room_service):
        self.room_service = room_service

    def __call__(self, value):
        """Check if a room with the given ID already exists."""
        if self.room_service.room_exists(value):
            raise ValidationError(f"Room with ID '{value}' already exists.")


async def validate_creating_private_room(data):
    if "room_password" not in data and data.room_type == RoomTypes.PRIVATE:
        raise ValidationError("Не задан пароль для приватной комнаты.")


async def validate_join_room(room_id: str, incoming_password: str = None):
    """
    Check if a user can join a room.
    """
    if not await RoomManager.room_exists_async(room_id):
        raise ValidationError(f"Room with ID '{room_id}' does not exist.")
    users = await RoomUserManager.get_users_in_room_async(room_id)
    room_data = await RoomManager.get_room_async(room_id)
    if len(users) >= room_data["max_users"]:
        raise ValidationError(f"Room with ID '{room_id}' is full.")
    room_type = room_data.get("room_type", False)
    if room_type == RoomTypes.PRIVATE:
        if incoming_password != room_data["room_password"]:
            raise ValueError("Неверный пароль для приватной комнаты.")

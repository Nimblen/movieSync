from rest_framework.exceptions import ValidationError


class UniqueRoomValidator:
    def __init__(self, room_service):
        self.room_service = room_service

    def __call__(self, value):
        """Check if a room with the given ID already exists."""
        if self.room_service.room_exists(value):
            raise ValidationError(f"Room with ID '{value}' already exists.")

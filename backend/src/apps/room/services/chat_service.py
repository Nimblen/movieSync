from src.apps.room.services.core import BaseService


class ChatService(BaseService):

    def get_messages(self, room_id: str, limit=50) -> list:
        return self.repository.get_list(
            f"room:{room_id}:messages", start=-limit, end=-1
        )

    def add_message(self, room_id: str, username: str, message: str, max_messages=100):
        key = f"room:{room_id}:messages"
        self.repository.push_to_list(key, f"{username}: {message}")
        self.repository.trim_list(key, -max_messages, -1)

    def clear_messages(self, room_id):
        self.repository.delete_key(f"room:{room_id}:messages")

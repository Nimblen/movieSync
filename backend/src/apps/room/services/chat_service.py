from src.apps.room.services.core import BaseService


class ChatService(BaseService):
    """Chat service supporting synchronous and asynchronous operations."""

    def get_messages_sync(self, room_id: str, limit=50) -> list:
        return self.repository.get_list_sync(
            f"room:{room_id}:messages", start=-limit, end=-1
        )

    def add_message_sync(self, room_id: str, username: str, message: str, max_messages=100):
        key = f"room:{room_id}:messages"
        self.repository.push_to_list_sync(key, f"{username}: {message}")
        self.repository.trim_list_sync(key, -max_messages, -1)

    def clear_messages_sync(self, room_id):
        self.repository.delete_key_sync(f"room:{room_id}:messages")

    async def get_messages_async(self, room_id: str, limit=50) -> list:
        return await self.repository.get_list_async(
            f"room:{room_id}:messages", start=-limit, end=-1
        )

    async def add_message_async(self, room_id: str, username: str, message: str, max_messages=100):
        key = f"room:{room_id}:messages"
        await self.repository.push_to_list_async(key, f"{username}: {message}")
        await self.repository.trim_list_async(key, -max_messages, -1)

    async def clear_messages_async(self, room_id):
        await self.repository.delete_key_async(f"room:{room_id}:messages")

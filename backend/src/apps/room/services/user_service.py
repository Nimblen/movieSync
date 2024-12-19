from src.apps.room.services.core import BaseService


class UserService(BaseService):

    def _get_user_key(self, room_id: str) -> str:
        return f"room:{room_id}:users"

    def add_user_to_room(self, room_id, username):
        self.repository.add_to_set_sync(self._get_user_key(room_id), username)

    def remove_user_from_room(self, room_id, username):
        self.repository.remove_from_set_sync(self._get_user_key(room_id), username)

    def get_users_in_room(self, room_id):
        return self.repository.get_set_sync(self._get_user_key(room_id))

    def clear_users(self, room_id):
        self.repository.delete_key_sync(self._get_user_key(room_id))


    async def add_user_to_room_async(self, room_id, username):
        await self.repository.add_to_set_async(self._get_user_key(room_id), username)

    async def remove_user_from_room_async(self, room_id, username):
        await self.repository.remove_from_set_async(self._get_user_key(room_id), username)

    async def get_users_in_room_async(self, room_id):
        return await self.repository.get_set_async(self._get_user_key(room_id))

    async def clear_users_async(self, room_id):
        await self.repository.delete_key_async(self._get_user_key(room_id))
from src.apps.room.services.core import BaseService


class UserService(BaseService):

    def _get_user_key(self, room_id: str) -> str:
        return f"room:{room_id}:users"

    def add_user_to_room(self, room_id, username):
        self.repository.add_to_set(self._get_user_key(room_id), username)

    def remove_user_from_room(self, room_id, username):
        self.repository.remove_from_set(self._get_user_key(room_id), username)

    def get_users_in_room(self, room_id):
        return self.repository.get_set(self._get_user_key(room_id))

    def clear_users(self, room_id):
        self.repository.delete_key(self._get_user_key(room_id))

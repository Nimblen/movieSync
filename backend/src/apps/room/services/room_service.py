class RoomService:
    def __init__(self, repository):
        self.repository = repository

    def create_room(self, data):
        if self.room_exists(data["room_id"]):
            raise ValueError(f"Room with ID {data['room_id']} already exists.")
        self.repository.set_hash(f"room:{data['room_id']}", data)
        return data

    def room_exists(self, room_id):
        return bool(self.repository.get_hash(f"room:{room_id}"))

    def get_room(self, room_id):
        room = self.repository.get_hash(f"room:{room_id}")
        if not room:
            raise ValueError(f"Room with ID {room_id} does not exist.")
        return room

    def get_rooms(self):
        keys = self.repository.get_hash_keys("room:*")
        rooms = [self.repository.get_hash(key) for key in keys]
        return rooms

    def delete_room(self, room_id):
        if not self.room_exists(room_id):
            raise ValueError(f"Room with ID {room_id} does not exist.")
        self.repository.delete_key(f"room:{room_id}")


class RoomStateService:
    def __init__(self, repository):
        self.repository = repository

    def get_room_state(self, room_id):
        state = self.repository.get_hash(f"room:{room_id}")
        if not state:
            raise ValueError(f"Room with ID {room_id} does not exist.")
        return state  # Возвращаем состояние как словарь

    def set_room_state(self, room_id, data):
        play = data.get("is_playing")
        if play:
            data["is_playing"] = 1
        else:
            data["is_playing"] = 0
        self.repository.set_hash(f"room:{room_id}", data)
        return data

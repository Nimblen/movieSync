class RoomService:
    def __init__(self, repository):
        self.repository = repository

    def create_room(self, data):
        if self.room_exists(data["room_id"]):
            raise ValueError(f"Room with ID {data['room_id']} already exists.")
        self.repository.set_hash_sync(f"room:{data['room_id']}", data)
        return data

    def room_exists(self, room_id):
        return bool(self.repository.get_hash_sync(f"room:{room_id}"))

    def get_room(self, room_id):
        room = self.repository.get_hash_sync(f"room:{room_id}")
        if not room:
            raise ValueError(f"Room with ID {room_id} does not exist.")
        return room

    def get_rooms(self):
        keys = self.repository.get_hash_keys_sync("room:*")
        rooms = []

        for key in keys:
            if self.repository.get_key_type_sync(key) == 'hash':
                rooms.append(self.repository.get_hash_sync(key))

        return rooms

    def delete_room(self, room_id):
        if not self.room_exists(room_id):
            raise ValueError(f"Room with ID {room_id} does not exist.")
        self.repository.delete_key(f"room:{room_id}")

    async def create_room_async(self, data):
        if self.room_exists(data["room_id"]):
            raise ValueError(f"Room with ID {data['room_id']} already exists.")
        await self.repository.set_hash_async(f"room:{data['room_id']}", data)
        return data
    

    async def room_exists_async(self, room_id):
        return bool(await self.repository.get_hash_async(f"room:{room_id}"))
    

    async def get_room_async(self, room_id):
        room = await self.repository.get_hash_async(f"room:{room_id}")        
        if not room:
            raise ValueError(f"Room with ID {room_id} does not exist.")
        return room
    

    async def get_rooms_async(self):
        keys = await self.repository.get_hash_keys_async("room:*")
        rooms = []

        for key in keys:
            if await self.repository.get_key_type_async(key) == 'hash':
                rooms.append(await self.repository.get_hash_async(key))

        return rooms
    

    async def delete_room_async(self, room_id):
        if not await self.room_exists_async(room_id):
            raise ValueError(f"Room with ID {room_id} does not exist.")
        await self.repository.delete_key_async(f"room:{room_id}")


class RoomStateService:
    def __init__(self, repository):
        self.repository = repository

    def get_room_state(self, room_id):
        state = self.repository.get_hash_sync(f"room:{room_id}")
        if not state:
            raise ValueError(f"Room with ID {room_id} does not exist.")
        return state  # Возвращаем состояние как словарь

    def set_room_state(self, room_id, data):
        current_state = self.get_room_state(room_id)
        new_state = data.copy()
        new_state["is_playing"] = 1 if data.get("is_playing") else 0
        if current_state == new_state:
            return {"success": False, "message": "State has not changed"}
        self.repository.set_hash_sync(f"room:{room_id}", new_state)
        return {"success": True, "state": new_state}
    
    async def get_room_state_async(self, room_id):
        state = await self.repository.get_hash_async(f"room:{room_id}")
        if not state:
            raise ValueError(f"Room with ID {room_id} does not exist.")
        return state
    
    async def set_room_state_async(self, room_id, data):
        current_state = await self.get_room_state_async(room_id)
        new_state = data.copy()
        new_state["is_playing"] = 1 if data.get("is_playing") else 0
        if current_state == new_state:
            return {"success": False, "message": "State has not changed"}
        await self.repository.set_hash_async(f"room:{room_id}", new_state)
        return {"success": True, "state": new_state}
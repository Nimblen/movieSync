




class RoomRepositoryInterface:
    def set_hash(self, key: str, data: dict) -> None:
        pass

    def get_hash(self, key: str) -> dict:
        pass

    def delete_key(self, key: str) -> None:
        pass

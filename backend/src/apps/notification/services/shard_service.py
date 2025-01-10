





class ShardService:
    def __init__(self, shard_count: int):
        self.shard_count = shard_count


    def get_shard(self, user_id: int) -> str:
        return f"all_users_shard_{user_id % self.shard_count}"
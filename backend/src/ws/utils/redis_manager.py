from src.ws.utils.redis_client import redis_client


class RoomRedisManager:
    @staticmethod
    def set_room_state(room_id, current_time, is_playing):
        """Set room state"""
        if is_playing:
            is_playing = "true"
        else:
            is_playing = "false"
        redis_client.hmset(
            f"room:{room_id}",
            {
                "current_time": current_time,
                "is_playing": is_playing,
            },
        )

    @staticmethod
    def get_room_state(room_id):
        """Get room state"""
        return redis_client.hgetall(f"room:{room_id}")

    @staticmethod
    def add_user_to_room(room_id, username):
        """Add user to room"""
        redis_client.sadd(f"room:{room_id}:users", username)

    @staticmethod
    def remove_user_from_room(room_id, username):
        """Delete user from room"""
        redis_client.srem(f"room:{room_id}:users", username)

    @staticmethod
    def get_users_in_room(room_id):
        """Return users in room"""
        return redis_client.smembers(f"room:{room_id}:users")

    @staticmethod
    def delete_room(room_id):
        """Delete room"""
        redis_client.delete(f"room:{room_id}")
        redis_client.delete(f"room:{room_id}:users")

    @staticmethod
    def add_message_to_room(room_id, username, message):
        """Add message to room"""
        redis_client.rpush(
            f"room:{room_id}:messages",
            f"{username}: {message}"
        )

    @staticmethod
    def get_room_messages(room_id, limit=50):
        """Get room messages"""
        return redis_client.lrange(f"room:{room_id}:messages", -limit, -1)

    @staticmethod
    def clear_room_messages(room_id):
        """Clear room messages"""
        redis_client.delete(f"room:{room_id}:messages")

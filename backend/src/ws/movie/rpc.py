from src.ws.utils.rpc_registry import rpc_method
from src.ws.utils.redis_manager import RoomRedisManager


@rpc_method
def get_initial_state(params):
    return {
        "success": True,
        "state": RoomRedisManager.get_room_state(params["room_id"]),
        "users": list(RoomRedisManager.get_users_in_room(params["room_id"])),
        "messages": RoomRedisManager.get_room_messages(
            params["room_id"], params.get("limit", 50)
        ),
        "type": "initial_state",
    }


@rpc_method
def set_sync_state(params):
    """
    set state
    """
    RoomRedisManager.set_room_state(
        params["room_id"], params["current_time"], params["is_playing"]
    )
    return {"success": True, "state": params, "type": "set_sync_state"}


@rpc_method
def get_sync_state(params):
    """
    get state
    """
    RoomRedisManager.get_room_state(params["room_id"])
    return {
        "success": True,
        "state": RoomRedisManager.get_room_state(params["room_id"]),
        "type": "get_sync_state",
    }


@rpc_method
def send_chat_message(params):
    RoomRedisManager.add_message_to_room(
        params["room_id"], params["username"], params["message"]
    )
    return {"success": True, "message": params["message"], "type": "chat_message"}


@rpc_method
def get_room_messages(params):
    return {
        "success": True,
        "messages": RoomRedisManager.get_room_messages(
            params["room_id"], params.get("limit", 50)
        ),
        "type": "get_room_messages",
    }

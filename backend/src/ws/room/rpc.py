from src.ws.utils.rpc_registry import rpc_method
from src.apps.room.services import RoomStateService, ChatService, UserService
from src.apps.core.repositories.redis_repository import RedisRepository


repository = RedisRepository()
RoomStateManager = RoomStateService(repository)
RoomUserManager = UserService(repository)
RoomMessageManager = ChatService(repository)

@rpc_method
async def get_initial_state(params):
    return {
        "success": True,
        "state": await RoomStateManager.get_room_state_async(params["room_id"]),
        "users": list(await RoomUserManager.get_users_in_room_async(params["room_id"])),
        "messages": await RoomMessageManager.get_messages_async(params["room_id"]),
        "type": "initial_state",
    }


@rpc_method
async def set_sync_state(params):
    """
    Set the synchronization state for the room.
    """
    current_state = await RoomStateManager.get_room_state_async(params["room_id"])

    current_time = float(current_state.get("current_time", 0))
    new_time = float(params.get("current_time", 0))

    if (
        abs(current_time - new_time) > 0.5  
        or current_state.get("is_playing") != params["is_playing"] 
    ):
        await RoomStateManager.set_room_state_async(params["room_id"], params)
        return {"success": True, "state": params, "type": "set_sync_state"}
    return {"success": True, "state": current_state, "type": "set_sync_state"}




@rpc_method
async def get_sync_state(params):
    """
    get state
    """ 
    state = await RoomStateManager.get_room_state_async(params["room_id"])
    return {
        "success": True,
        "state": state,
        "type": "get_sync_state",
    }


@rpc_method
async def send_chat_message(params):
    await RoomMessageManager.add_message_async(
        params["room_id"], params["username"], params["message"]
    )
    return {"success": True, "message": params["message"], "type": "chat_message"}


@rpc_method
async def get_room_messages(params):
    return {
        "success": True,
        "messages": await RoomMessageManager.get_messages_async(
            params["room_id"], params.get("limit", 50)
        ),
        "type": "get_room_messages",
    }

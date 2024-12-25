from src.apps.core.utils.rpc_registry import rpc_method
from src.apps.room.services import RoomMessageManager



@rpc_method
async def send_chat_message(params):
    await RoomMessageManager.add_message_async(
        params["room_id"], params["username"], params["message"]
    )
    return params


@rpc_method
async def get_room_messages(params):
    return await RoomMessageManager.get_messages_async(params["room_id"])


@rpc_method
async def clear_room_messages(params):
    await RoomMessageManager.clear_messages_async(params["room_id"])
    return {"result": "messages cleared"}

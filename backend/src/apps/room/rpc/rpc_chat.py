from src.apps.core.utils.rpc_registry import rpc_method
from src.apps.room.services import RoomMessageManager
from src.apps.core.utils.rpc_responses import make_rpc_response


@rpc_method
async def send_chat_message(params):
    await RoomMessageManager.add_message_async(
        params["room_id"], params["username"], params["message"]
    )
    return make_rpc_response(params, params.get("id", 1))


@rpc_method
async def get_room_messages(params):
    return make_rpc_response(
        await RoomMessageManager.get_messages(params["room_id"]), params.get("id", 1)
    )


@rpc_method
async def clear_room_messages(params):
    await RoomMessageManager.clear_messages_async(params["room_id"])
    return make_rpc_response("chat messages cleared", params.get("id", 1))

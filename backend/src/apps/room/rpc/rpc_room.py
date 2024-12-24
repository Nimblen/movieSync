from src.apps.core.utils.rpc_registry import rpc_method
from src.apps.core.utils.rpc_responses import make_rpc_response, make_rpc_error
from src.apps.room.serializers.room import RoomSerializer
from src.apps.room.services import *



@rpc_method
async def get_initial_state(params):
    return {
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
        return params
    return current_state




@rpc_method
async def get_sync_state(params):
    """
    get state
    """ 
    return await RoomStateManager.get_room_state_async(params["room_id"])


@rpc_method
async def create_room(params):
    '''
    Create a new room.'''
    serializer = RoomSerializer(data=params)
    if not serializer.is_valid():
        return make_rpc_error(400, serializer.errors, params.get("id", 1))
    await RoomManager.create_room_async(params)
    return params


@rpc_method
async def delete_room(params):
    try:
        await RoomManager.delete_room_async(params["room_id"])
        return params
    except Exception as e:
        return make_rpc_error(400, str(e), params.get("id", 1))
    

@rpc_method
async def get_rooms(params):
    return await RoomManager.get_rooms_async()


@rpc_method
async def get_room(params):
    return await RoomManager.get_room_async(params["room_id"])
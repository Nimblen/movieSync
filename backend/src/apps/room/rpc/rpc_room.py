from src.apps.core.utils.rpc_registry import rpc_method
from src.apps.core.utils.rpc_responses import make_rpc_error, make_rpc_response
from src.apps.room.serializers.room import RoomSerializer
from src.apps.notification.services.notification_service import Notifier
from src.apps.room.validators.room_validator import (
    validate_join_room,
    validate_creating_private_room,
)
from src.apps.room.services import *


@rpc_method
async def join_room(params):
    consumer = params.pop("consumer")
    room_id = params["room_id"]
    try:
        if consumer.room_id:
            await RoomUserManager.remove_user_from_room_async(
                consumer.room_id, consumer.user.username
            )
            await consumer.channel_layer.group_discard(
                f"room_{consumer.room_id}", consumer.channel_name
            )
            await consumer.notifier.send_to_room(
                consumer.room_id,
                consumer.notifier.create_notification_message(
                    f"User {consumer.user.username} left the room", "user_left"
                ),
            )
        await validate_join_room(room_id)
        await RoomUserManager.add_user_to_room_async(room_id, consumer.user.username)
        consumer.room_id = room_id
        consumer.group_name = f"room_{room_id}"
        await consumer.channel_layer.group_add(
            consumer.group_name, consumer.channel_name
        )

        await consumer.notifier.send_to_room(
            room_id,
            consumer.notifier.create_notification_message(
                f"User {consumer.user.username} joined the room", "user_joined"
            ),
        )
        return params
    except Exception as e:
        return make_rpc_error(400, str(e), params.get("id", 1))


@rpc_method
async def leave_room(params):
    consumer = params.pop("consumer")
    room_id = consumer.room_id
    try:
        if room_id:
            username = consumer.user.username
            await RoomUserManager.remove_user_from_room_async(room_id, username)
            await consumer.channel_layer.group_discard(
                f"room_{room_id}", consumer.channel_name
            )
            await consumer.notifier.send_to_room(
                consumer.room_id,
                consumer.notifier.create_notification_message(
                    f"User {consumer.user.username} left the room", "user_left"
                ),
            )
            consumer.room_id = None
            return params
    except Exception as e:
        return make_rpc_error(400, str(e), params.get("id", 1))


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
    """
    Create a new room."""
    try:
        RoomSerializer(data=params)
        await validate_creating_private_room(params)
        await RoomManager.create_room_async(params)
        return params
    except Exception as e:
        return make_rpc_error(400, str(e), params.get("id", 1))


@rpc_method
async def delete_room(params):
    try:
        await RoomManager.delete_room_async(params["room_id"])
        return params
    except Exception as e:
        return make_rpc_error(400, str(e), params.get("id", 1))


@rpc_method
async def get_rooms(params):
    rooms = await RoomManager.get_rooms_async()
    serializer = RoomSerializer(rooms, many=True)
    return {"status": "success", "rooms": serializer.data}


@rpc_method
async def get_room(params):
    room = await RoomManager.get_room_async(params["room_id"])
    serializer = RoomSerializer(room)
    return {"status": "success", "room": serializer.data}

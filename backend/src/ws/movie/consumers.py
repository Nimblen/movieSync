import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from src.ws.utils.redis_manager import RoomRedisManager
import logging
from src.ws.movie.handlers import handle_rpc_request
from src.ws.movie.rpc import *

logger = logging.getLogger(__name__)


class MovieStateConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):

        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.group_name = f"movie_state_{self.room_name}"
        self.username = self.scope["user"].username

        # if self.scope["user"].is_anonymous:
        #     await self.close()
        #     logger.warning("Anonymous user tried to connect to WebSocket.")
        #     return

        RoomRedisManager.add_user_to_room(self.room_name, self.username)

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        logger.info(f"User {self.username} connected to room {self.room_name}.")




    async def disconnect(self, close_code):
        if hasattr(self, "room_name") and hasattr(self, "username"):
            RoomRedisManager.remove_user_from_room(self.room_name, self.username)
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

            users = RoomRedisManager.get_users_in_room(self.room_name)
            if not users:
                RoomRedisManager.delete_room(self.room_name)
                logger.info(f"Room {self.room_name} deleted. All users left.")
            else:
                logger.info(
                    f"User {self.username} disconnected from room {self.room_name}."
                )
        else:
            logger.warning("disconnect called without valid room_name or username.")

    async def receive_json(self, content):
        content["params"]["username"] = self.username or "noName"
        response = handle_rpc_request(content)

        if "result" in response:
            if response["result"].get("type") in ["set_sync_state", "chat_message"]:
                await self.channel_layer.group_send(
                    self.group_name,
                    {"type": "broadcast_message", "response": response},
                )
            else:
                await self.send_json(response)
        else:
            await self.send_json(response)

    async def broadcast_message(self, event):
        await self.send_json(event["response"])

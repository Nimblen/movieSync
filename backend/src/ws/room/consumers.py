from channels.generic.websocket import AsyncJsonWebsocketConsumer
import logging
from src.apps.room.services import RoomService, UserService
from src.apps.core.repositories.redis_repository import RedisRepository
from src.ws.room.handlers import handle_rpc_request
from src.ws.room.rpc import *

logger = logging.getLogger(__name__)

repository = RedisRepository()
room_service = RoomService(repository)
user_service = UserService(repository)


class MovieStateConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        try:
            self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
            self.group_name = f"movie_state_{self.room_name}"
            self.username = self.scope["user"].username
        except KeyError as e:
            logger.error(f"Missing required scope keys during WebSocket connect: {e}")
            await self.close()
            return

        if not room_service.room_exists(self.room_name):
            logger.warning(f"Room {self.room_name} does not exist. Closing connection.")
            await self.close()
            return

        user_service.add_user_to_room(self.room_name, self.username)

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        logger.info(f"User {self.username} connected to room {self.room_name}.")

    async def disconnect(self, close_code):
        if hasattr(self, "room_name") and hasattr(self, "username"):
            user_service.remove_user_from_room(self.room_name, self.username)
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
            logger.info(f"User {self.username} disconnected from room {self.room_name}.")

    async def receive_json(self, content):
        try:
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
        except Exception as e:
            logger.exception(f"Error processing message: {content}. Exception: {e}")
            await self.send_json(
                {
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32603,
                        "message": "Internal error",
                        "data": str(e),
                    },
                    "id": content.get("id"),
                }
            )

    async def broadcast_message(self, event):
        await self.send_json(event["response"])

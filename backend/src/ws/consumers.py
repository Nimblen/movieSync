from channels.generic.websocket import AsyncJsonWebsocketConsumer
import logging
from src.ws.handlers import handle_rpc_request
from src.apps.core.utils.rpc_responses import make_rpc_error
from src.apps.room.services import *
from src.apps.room.rpc import *


logger = logging.getLogger(__name__)





class MainConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        try:
            user = self.scope["user"]
            # if isinstance(user, AnonymousUser) or not user.is_authenticated:
            #     logger.warning("Attempt to connect by anonymous user. Closing...")
            #     await self.close()
            #     return
            self.username = user.username
            self.room_name = self.scope["url_route"]["kwargs"].get("room_name")
            if self.room_name:
                room_exists = await RoomManager.room_exists_async(self.room_name)
                if not room_exists:
                    logger.warning(f"Room '{self.room_name}' does not exist. Closing connection.")
                    await self.close()
                    return
                self.group_name = f"room_{self.room_name}"
                await RoomUserManager.add_user_to_room_async(self.room_name, self.username)
                await self.channel_layer.group_add(self.group_name, self.channel_name)
            else:
                self.group_name = None
            await self.channel_layer.group_add(f"notification_{self.username}", self.channel_name)
            await self.accept()

            logger.info(f"User '{self.username}' connected. Room: {self.room_name or 'No room'}")

        except KeyError as e:
            logger.error(f"Missing required scope keys during WebSocket connect: {e}")
            await self.close()

    async def disconnect(self, close_code):
        if hasattr(self, "room_name") and hasattr(self, "username") and self.room_name and self.group_name:
            await RoomUserManager.remove_user_from_room_async(self.room_name, self.username)
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
            logger.info(f"User '{self.username}' disconnected from room '{self.room_name}'. Code={close_code}")
        if hasattr(self, "username"):
            await self.channel_layer.group_discard(f"notification_{self.username}", self.channel_name)

    async def receive_json(self, content, **kwargs):
        try:
            params = content.get("params", {})
            params["username"] = getattr(self, "username", "noName")
            content["params"] = params
            response = await handle_rpc_request(content)
            if "result" in response:
                result_type = response["result"].get("type")
                if result_type in ["set_sync_state", "chat_message"]:
                    if self.group_name:
                        await self.channel_layer.group_send(
                            self.group_name,
                            {"type": "broadcast_message", "response": response},
                        )
                    else:
                        await self.send_json(response)
                else:
                    await self.send_json(response)
            else:
                await self.send_json(response)

        except Exception as e:
            logger.exception(f"Error processing message: {content}. Exception: {e}")
            rpc_id = content.get("id", 1)
            await self.send_json(make_rpc_error(500, str(e), rpc_id))

    async def broadcast_message(self, event):
        await self.send_json(event["response"])

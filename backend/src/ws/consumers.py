from channels.generic.websocket import AsyncJsonWebsocketConsumer
import logging
from src.ws.handlers import handle_rpc_request
from src.apps.core.utils.rpc_responses import make_rpc_error
from src.apps.core.constants import SHARD_COUNT
from src.apps.notification.services import ShardService, Notifier
from src.apps.room.services import *
from src.apps.room.rpc import *
from src.apps.movie.rpc import *


logger = logging.getLogger(__name__)





class MainConsumer(AsyncJsonWebsocketConsumer):
    shard_manager = ShardService(SHARD_COUNT)
    async def connect(self):
        try:
            self.user = self.scope["user"]
            if self.user.is_anonymous:
                logger.warning("Attempt to connect by anonymous user. Closing...")
                await self.close()
                return
            self.notifier = Notifier(self.channel_layer)
            await self.channel_layer.group_add(f"notification_{self.user.username}", self.channel_name)
            shard_group = self.shard_manager.get_shard(self.user.id)
            await self.channel_layer.group_add(shard_group, self.channel_name)
            await self.notifier.send_to_all_users(self.notifier.create_notification_message("This site is in test mode."))
            self.room_id = None
            await self.accept()

        except KeyError as e:
            logger.error(f"Missing required scope keys during WebSocket connect: {e}")
            await self.close()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(f"notification_{self.user.username}", self.channel_name)
        shard_group = self.shard_manager.get_shard(self.user.id)
        await self.channel_layer.group_discard(shard_group, self.channel_name)
        if self.room_id:
            await self.channel_layer.group_discard(f"room_{self.room_id}", self.channel_name)
            await RoomUserManager.remove_user_from_room_async(self.room_id, self.user.username)

    async def receive_json(self, content, **kwargs):
        try:
            params = content.get("params", {})
            params["username"] = self.user.username or "Anonymous"
            content["params"] = params
            content["consumer"] = self
            response = await handle_rpc_request(content)
            if "result" in response:
                result_type = response["result"].get("type")
                if result_type in ["set_sync_state", "chat_message"]:
                    if self.room_id:
                        await self.channel_layer.group_send(
                            self.room_id,
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

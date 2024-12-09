import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from .rpc import handle_rpc_request

class MovieStateConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        if self.scope["user"].is_anonymous:
            await self.close()
            return

        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.group_name = f"movie_state_{self.room_name}"

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive_json(self, content):

        response = handle_rpc_request(json.dumps(content))


        if "result" in response:
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "broadcast_message",
                    "message": response["result"]
                }
            )

        await self.send_json(response)

    async def broadcast_message(self, event):
        await self.send_json({
            "type": "broadcast",
            "message": event["message"]
        })

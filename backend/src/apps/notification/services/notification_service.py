import asyncio
import logging
from typing import Optional, Dict
from src.apps.core.utils.rpc_responses import make_rpc_response
from src.apps.core.constants import (
    SHARD_COUNT,
    NotificationGroupTypes,
    NotificationLevels,
    NotificationPrefix,
)

logger = logging.getLogger(__name__)


class Notifier:
    def __init__(self, channel_layer):
        self.channel_layer = channel_layer

    async def send_to_group(
        self, group_name: str, event_type: str, data: Dict, request_id: int
    ) -> None:
        """
        Sends a notification to a specific group.
        """
        try:
            message = {
                "type": "broadcast_message",
                "response": make_rpc_response(
                    {
                        "type": event_type,
                        **data,
                    },
                    request_id=request_id,
                ),
            }
            await self.channel_layer.group_send(group_name, message)
            logger.debug(f"Sent message to group {group_name}: {event_type}")
        except Exception as e:
            logger.error(
                f"Failed to send message to group {group_name}: {e}", exc_info=True
            )

    async def send_notification(
        self,
        data: Dict,
        group_type: NotificationGroupTypes = NotificationGroupTypes.ALL,
        identifier: Optional[str] = None,
        event_type: str = "broadcast_message",
        request_id: Optional[int] = None,
    ) -> None:
        """
        Notifies users in the specified group.
        """
        if group_type == NotificationGroupTypes.ALL:
            tasks = [
                self.send_to_group(
                    f"all_users_shard_{shard_id}", event_type, data, request_id
                )
                for shard_id in range(SHARD_COUNT)
            ]
            await asyncio.gather(*tasks)
        elif group_type == NotificationGroupTypes.ROOM:
            if not identifier:
                raise ValueError(
                    "Необходимо предоставить room_id для уведомлений комнаты."
                )
            group_name = f"room_{identifier}"
            await self.send_to_group(group_name, event_type, data, request_id)
        elif group_type == NotificationGroupTypes.INDIVIDUAL:
            if not identifier:
                raise ValueError(
                    "Необходимо предоставить username для индивидуальных уведомлений."
                )
            group_name = f"notification_{identifier}"
            await self.send_to_group(group_name, event_type, data, request_id)
        else:
            raise ValueError(f"Не поддерживаемый тип группы: {group_type}")

    async def send_to_all_users(
        self, data: Dict, request_id: Optional[int] = None
    ) -> None:
        """
        Sends a notification to all users.

        :param data: Notification data.
        :param request_id: Request ID.
        """
        await self.send_notification(
            data,
            group_type=NotificationGroupTypes.ALL,
            request_id=request_id,
        )

    async def send_to_room(
        self, room_id: str, data: Dict, request_id: Optional[int] = None
    ) -> None:
        """
        Sends a notification to a specific room.

        :param room_id: Room ID.
        :param data: Notification data.
        :param request_id: Request ID.
        """
        await self.send_notification(
            data,
            group_type=NotificationGroupTypes.ROOM,
            identifier=room_id,
            request_id=request_id,
        )

    async def send_to_user(
        self, username: str, data: Dict, request_id: Optional[int] = None
    ) -> None:
        """
        Sends a notification to a specific user.

        :param username: Username.
        :param data: Notification data.
        :param request_id: Request ID.
        """
        await self.send_notification(
            data,
            group_type=NotificationGroupTypes.INDIVIDUAL,
            identifier=username,
            request_id=request_id,
        )

    def create_notification_message(
        self,
        message: str,
        message_type: str = "notification",
        notification_level: NotificationLevels = NotificationLevels.INFO,
        notification_prefix: NotificationPrefix = NotificationPrefix.SERVER,
    ) -> Dict:
        """
        Creates a structured notification message.

        :param message: The content of the notification.
        :param message_type: The type of the message.
        :param notification_level: The level of the notification (INFO, WARNING, ERROR).
        :param notification_prefix: The prefix of the notification (SERVER, ADMIN, CREATOR).
        :return: A dictionary representing the notification message.
        """
        return {
            "message": message,
            "type": message_type,
            "level": notification_level.value,
            "prefix": notification_prefix.value,
        }

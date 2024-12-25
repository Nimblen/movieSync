from src.apps.core.repositories.redis_repository import RedisRepository
from .chat_service import ChatService
from .room_service import RoomService, RoomStateService
from .user_service import UserService


repository = RedisRepository()
RoomManager = RoomService(repository)
RoomStateManager = RoomStateService(repository)
RoomUserManager = UserService(repository)
RoomMessageManager = ChatService(repository)

__all__ = ["RoomManager", "RoomStateManager", "RoomUserManager", "RoomMessageManager"]
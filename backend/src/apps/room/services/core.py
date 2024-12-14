from src.apps.core.repositories.core import RoomRepositoryInterface
from src.apps.core.repositories.redis_repository import RedisRepository

class BaseService:
    def __init__(self, repository: RoomRepositoryInterface):
        self.repository = repository

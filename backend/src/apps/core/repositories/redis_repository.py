from typing import Any, Dict, List
from src.apps.core.utils.redis_client import redis_client
from src.apps.core.repositories.core import RoomRepositoryInterface


class RedisRepository(RoomRepositoryInterface):
    """Redis repository class."""

    @staticmethod
    def set_hash(key: str, mapping: Dict[str, Any]) -> None:
        '''Add mapping to hash with given key'''
        redis_client.hset(key, mapping=mapping)

    @staticmethod
    def trim_list(key: str, start: int, end: int):
        '''Trim list with given key'''
        redis_client.ltrim(key, start, end)

    @staticmethod
    def get_hash(key: str) -> Dict[str, Any]:
        '''Get hash with given key'''
        return redis_client.hgetall(key)
    
    @staticmethod
    def get_hash_keys(pattern: str) -> List[str]:
        '''Get hash keys with given pattern'''
        return redis_client.keys(pattern)

    @staticmethod
    def set_value(key: str, value: Any) -> None:
        '''Set value to key'''
        redis_client.set(key, value)

    @staticmethod
    def get_value(key: str) -> Any:
        '''Get value from key'''
        return redis_client.get(key)

    @staticmethod
    def add_to_set(key: str, value: str) -> None:
        '''Add value to set with given key, unique values'''
        redis_client.sadd(key, value)


    @staticmethod
    def remove_from_set(key: str, value: str) -> None:
        '''Remove value from set with given key'''
        redis_client.srem(key, value)

    @staticmethod
    def get_set(key: str) -> List[str]:
        '''Get set with given key'''
        return redis_client.smembers(key)

    @staticmethod
    def push_to_list(key: str, value: str) -> None:
        '''Push value to list with given key'''
        redis_client.rpush(key, value)

    @staticmethod
    def get_list(key: str, start: int = 0, end: int = -1) -> List[str]:
        '''Get list with given key'''
        return redis_client.lrange(key, start, end)

    @staticmethod
    def delete_key(key: str) -> None:
        '''Delete key'''
        redis_client.delete(key)

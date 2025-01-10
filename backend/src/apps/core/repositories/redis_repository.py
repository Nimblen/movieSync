from typing import Any, Dict, List

from src.apps.core.utils.redis_client import async_redis_client, sync_redis_client
from src.apps.core.repositories.core import RoomRepositoryInterface


class RedisRepository(RoomRepositoryInterface):
    """Redis repository class."""

    # --- СИНХРОННЫЕ МЕТОДЫ ---
    @staticmethod
    def set_hash_sync(key: str, mapping: Dict[str, Any]) -> None:
        """Add mapping to hash with given key (synchronously)"""
        sync_redis_client.hset(key, mapping=mapping)

    @staticmethod
    def trim_list_sync(key: str, start: int, end: int):
        """Trim list with given key (synchronously)"""
        sync_redis_client.ltrim(key, start, end)

    @staticmethod
    def get_hash_sync(key: str) -> Dict[str, Any]:
        """Get hash with given key (synchronously)"""
        return sync_redis_client.hgetall(key)

    @staticmethod
    def get_hash_keys_sync(pattern: str) -> List[str]:
        """Get hash keys with given pattern (synchronously)"""
        return sync_redis_client.keys(pattern)

    @staticmethod
    def set_value_sync(key: str, value: Any) -> None:
        """Set value to key (synchronously)"""
        sync_redis_client.set(key, value)

    @staticmethod
    def get_value_sync(key: str) -> Any:
        """Get value from key (synchronously)"""
        return sync_redis_client.get(key)

    @staticmethod
    def add_to_set_sync(key: str, value: str) -> None:
        """Add value to set with given key (synchronously)"""
        sync_redis_client.sadd(key, value)

    @staticmethod
    def remove_from_set_sync(key: str, value: str) -> None:
        """Remove value from set with given key (synchronously)"""
        sync_redis_client.srem(key, value)

    @staticmethod
    def get_set_sync(key: str) -> List[str]:
        """Get set with given key (synchronously)"""
        return sync_redis_client.smembers(key)

    @staticmethod
    def push_to_list_sync(key: str, value: str) -> None:
        """Push value to list with given key (synchronously)"""
        sync_redis_client.rpush(key, value)

    @staticmethod
    def get_list_sync(key: str, start: int = 0, end: int = -1) -> List[str]:
        """Get list with given key (synchronously)"""
        return sync_redis_client.lrange(key, start, end)

    @staticmethod
    def delete_key_sync(key: str) -> None:
        """Delete key (synchronously)"""
        sync_redis_client.delete(key)

    @staticmethod
    def get_key_type_sync(key: str) -> str:
        """Get key type (synchronously)"""
        return sync_redis_client.type(key)

    # --- АСИНХРОННЫЕ МЕТОДЫ ---
    @staticmethod
    async def set_hash_async(key: str, mapping: Dict[str, Any]) -> None:
        """Add mapping to hash with given key (asynchronously)"""
        await async_redis_client.hset(key, mapping=mapping)

    @staticmethod
    async def trim_list_async(key: str, start: int, end: int):
        """Trim list with given key (asynchronously)"""
        await async_redis_client.ltrim(key, start, end)

    @staticmethod
    async def get_hash_async(key: str) -> Dict[str, Any]:
        """Get hash with given key (asynchronously)"""
        return await async_redis_client.hgetall(key)

    @staticmethod
    async def get_hash_keys_async(pattern: str) -> List[str]:
        """Get hash keys with given pattern (asynchronously)"""
        return await async_redis_client.keys(pattern)

    @staticmethod
    async def set_value_async(key: str, value: Any) -> None:
        """Set value to key (asynchronously)"""
        await async_redis_client.set(key, value)

    @staticmethod
    async def get_value_async(key: str) -> Any:
        """Get value from key (asynchronously)"""
        return await async_redis_client.get(key)

    @staticmethod
    async def add_to_set_async(key: str, value: str) -> None:
        """Add value to set with given key (asynchronously)"""
        await async_redis_client.sadd(key, value)

    @staticmethod
    async def remove_from_set_async(key: str, value: str) -> None:
        """Remove value from set with given key (asynchronously)"""
        await async_redis_client.srem(key, value)

    @staticmethod
    async def get_set_async(key: str) -> List[str]:
        """Get set with given key (asynchronously)"""
        return await async_redis_client.smembers(key)

    @staticmethod
    async def push_to_list_async(key: str, value: str) -> None:
        """Push value to list with given key (asynchronously)"""
        await async_redis_client.rpush(key, value)

    @staticmethod
    async def get_list_async(key: str, start: int = 0, end: int = -1) -> List[str]:
        """Get list with given key (asynchronously)"""
        return await async_redis_client.lrange(key, start, end)

    @staticmethod
    async def delete_key_async(key: str) -> None:
        """Delete key (asynchronously)"""
        await async_redis_client.delete(key)

    @staticmethod
    async def get_key_type_async(key: str) -> str:
        """Get key type (asynchronously)"""
        return await async_redis_client.type(key)

from redis.asyncio import Redis as AsyncRedis
from redis import Redis as SyncRedis

from config import settings

# Синхронный клиент
sync_redis_client = SyncRedis(
    host=settings.REDIS_CONFIG["host"],
    port=settings.REDIS_CONFIG["port"],
    db=settings.REDIS_CONFIG["db"],
    decode_responses=settings.REDIS_CONFIG["decode_responses"]
)

# Асинхронный клиент
async_redis_client = AsyncRedis.from_url(
    f"redis://{settings.REDIS_CONFIG['host']}:{settings.REDIS_CONFIG['port']}/{settings.REDIS_CONFIG['db']}",
    decode_responses=settings.REDIS_CONFIG["decode_responses"]
)

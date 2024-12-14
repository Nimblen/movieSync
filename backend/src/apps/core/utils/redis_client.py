import redis
from config import settings

redis_client = redis.StrictRedis(
    host=settings.REDIS_CONFIG["host"],
    port=settings.REDIS_CONFIG["port"],
    db=settings.REDIS_CONFIG["db"],
    decode_responses=settings.REDIS_CONFIG["decode_responses"],
)
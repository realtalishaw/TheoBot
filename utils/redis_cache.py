# utils/cache.py

import redis
from os import getenv

# Initialize Redis client
REDIS_HOST = getenv("REDIS_HOST", "localhost")
REDIS_PORT = getenv("REDIS_PORT", 6379)
REDIS_PASSWORD = getenv("REDIS_PASSWORD", None)  # Use None if no password is set
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, decode_responses=True)

# Function to get data from cache
def get_from_cache(key):
    try:
        return redis_client.get(key)
    except redis.RedisError as e:
        print(f"Redis error: {e}")
        return None  # In case of error, return None

# Function to set data in cache
def set_in_cache(key, value, timeout=3600):  # Default timeout of 1 hour
    try:
        redis_client.set(key, value, ex=timeout)
    except redis.RedisError as e:
        print(f"Redis error: {e}")

# Additional functions to handle specific cache operations can be added here

# models/user_cache.py

import json
from utils.redis_cache import get_from_cache, set_in_cache

# Function to serialize user data for caching
def serialize_user_data(user):
    return json.dumps(user, default=str)  # default=str to handle non-serializable data

# Function to deserialize user data from cache
def deserialize_user_data(user_data):
    return json.loads(user_data)

def get_user_by_id(user_id):
    key = f"user:{user_id}"
    user_data = get_from_cache(key)
    if user_data:
        return deserialize_user_data(user_data)
    
    # If not in cache, fetch from database/API and cache it
    response = your_api_call_function_to_get_user_by_id(user_id)  # Replace with your actual API call function
    if response.ok:
        user = response.json()
        set_in_cache(key, serialize_user_data(user))
        return user
    else:
        response.raise_for_status()

def set_user_by_id(user_id, user):
    key = f"user:{user_id}"
    set_in_cache(key, serialize_user_data(user))

def update_user_by_id(user_id, update_data):
    # Update the user in the database/API
    response = your_api_call_function_to_update_user_by_id(user_id, update_data)  # Replace with your actual API call function
    if response.ok:
        user = response.json()
        set_user_by_id(user_id, user)  # Update the cache with new data
        return user
    else:
        response.raise_for_status()

# Add additional functions to delete user, list all users, verify user, etc., as needed

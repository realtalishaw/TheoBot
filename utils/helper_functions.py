from utils.redis_cache import get_from_cache, set_in_cache

def is_user_allowed(update, context):
    """
    Check if the user is allowed to use the bot.

    Args:
        update (telegram.Update): The update object containing information about the incoming message.
        context (telegram.ext.CallbackContext): The context object for the handler.

    Returns:
        bool: True if the user is allowed, False otherwise.
    """
    user_id = update.message.from_user.id
    user_data = get_from_cache(str(user_id))

    if user_data is None or user_data == 'unconfirmed':
        update.message.reply_text("Please register with /start to use the bot.")
        return False
    return True
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from dotenv import load_dotenv
import os
from utils.logger import setup_logger

load_dotenv()
telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
logger = setup_logger(__name__, 'bot.log')

def start(update, context):
    """Send a message when the command /start is issued."""
    logger.info('User %s started the bot.', update.message.from_user.first_name)
    update.message.reply_text('Hello, World!')
    
def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main():
    """Start the bot."""
    logger.info("Bot is starting...")  # Log that the bot is starting
    # Create the Updater and pass it your bot's token.
    updater = Updater(telegram_bot_token, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()

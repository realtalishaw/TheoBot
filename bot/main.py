from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from dotenv import load_dotenv
import os
from utils.logger import setup_logger
from bot import commands

load_dotenv()
telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
logger = setup_logger(__name__, 'bot.log')

    

def text_message_handler(update, context):
    """Handle regular text messages."""
    text_received = update.message.text
    logger.info(f'Received message: {text_received}')
    # Here you can implement more complex functionality or AI integration.
    update.message.reply_text('You said: ' + text_received)


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)  

def main():
    """Start the bot."""
    logger.info("Bot is starting...")  # Log that the bot is starting
    updater = Updater(telegram_bot_token, use_context=True)
    dp = updater.dispatcher

    # Register handlers from the commands module
    dp.add_handler(CommandHandler("start", commands.start))
    dp.add_handler(CommandHandler("help", commands.help))
    dp.add_handler(CommandHandler("register", commands.register))
    dp.add_handler(CommandHandler("project", commands.project))
    dp.add_handler(CommandHandler("assignrole", commands.assignrole))
    dp.add_handler(CommandHandler("createtask", commands.createtask))
    dp.add_handler(CommandHandler("assigntask", commands.assigntask))
    dp.add_handler(CommandHandler("status", commands.status))
    dp.add_handler(CommandHandler("calendar", commands.calendar))
    dp.add_handler(CommandHandler("addevent", commands.addevent))
    dp.add_handler(CommandHandler("rsvp", commands.rsvp))
    dp.add_handler(CommandHandler("settings", commands.settings))
    dp.add_handler(CommandHandler("feedback", commands.feedback))
    
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, text_message_handler))
    dp.add_handler(CallbackQueryHandler(commands.button))
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()

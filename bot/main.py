from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
import os
from dotenv import load_dotenv
from utils.logger import setup_logger
from bot.conversation_handler import chat_with_openai
from bot.commands.commands import start, help, register, project, assignrole, createtask, assigntask, status, calendar, addevent, rsvp, settings, feedback, button, conv_handler

load_dotenv()
telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
logger = setup_logger(__name__, 'bot.log')



def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)  

def main():
    updater = Updater(telegram_bot_token, use_context=True)
    dp = updater.dispatcher

    # Register command handlers

    dp.add_handler(conv_handler)
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("register", register))
    dp.add_handler(CommandHandler("project", project))
    dp.add_handler(CommandHandler("assignrole", assignrole))
    dp.add_handler(CommandHandler("createtask", createtask))
    dp.add_handler(CommandHandler("assigntask", assigntask))
    dp.add_handler(CommandHandler("status", status))
    dp.add_handler(CommandHandler("calendar", calendar))
    dp.add_handler(CommandHandler("addevent", addevent))
    dp.add_handler(CommandHandler("rsvp", rsvp))
    dp.add_handler(CommandHandler("settings", settings))
    dp.add_handler(CommandHandler("feedback", feedback))
    #dp.add_handler(CommandHandler("end", end))

    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, chat_with_openai))

    # Register callback query handler for button interactions
    dp.add_handler(CallbackQueryHandler(button))

    # Register error handler
    dp.add_error_handler(error)

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
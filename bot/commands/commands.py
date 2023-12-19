from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler, CallbackContext
from utils.redis_cache import get_from_cache, set_in_cache
from utils.helper_functions import is_user_allowed
import re

# Define states for the conversation
EMAIL, PHONE, BIO, ONBOARDING, WATCH_VIDEO, QUIZ = range(6)

# Define quiz questions and answers
quiz_questions = [
    ("What is 2+2?", ["4", "22"], "4"),
    ("Who is the president of the United States:", ["Trump", "Biden", "IDK"], "Biden"),
    ("What color is the Sky?", ["Pink", "Orange", "Blue"], "Blue")
]

# Define the callback data for the buttons
BEGIN_ONBOARDING_CALLBACK_DATA = 'begin_onboarding'

# Email validation regex
EMAIL_REGEX = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

def start(update: Update, context: CallbackContext) -> int:
    user_id = update.message.from_user.id
    user_name = update.message.from_user.first_name  # Retrieving the user's first name
    user_data = get_from_cache(str(user_id))
    
    if user_data is None:
        update.message.reply_text(f'Welcome {user_name}! Please enter your email:')
        return EMAIL
    elif user_data == 'unconfirmed':
        # The user exists but isn't confirmed. Prompt them to wait or contact an admin.
        update.message.reply_text("Your registration is pending approval. You cannot access the bot at this moment.")
    else:
        # The user is confirmed. Proceed with the normal welcome message.
        update.message.reply_text('Welcome back to TheoBot! Type /help for a list of commands.')

def collect_email(update: Update, context: CallbackContext) -> int:
    email = update.message.text
    if re.fullmatch(EMAIL_REGEX, email):
        context.user_data['email'] = email
        update.message.reply_text('Great! Now, please send me your phone number.')
        return PHONE
    else:
        update.message.reply_text('Invalid email. Please enter a valid email address:')
        return EMAIL

def collect_phone(update: Update, context: CallbackContext) -> int:
    phone = update.message.text
    if phone.isdigit() and 7 <= len(phone) <= 15:  # Basic validation for phone number
        context.user_data['phone'] = phone
        update.message.reply_text('Thanks! Lastly, tell me a bit about yourself.')
        return BIO
    else:
        update.message.reply_text('Invalid phone number. Please enter a valid phone number:')
        return PHONE

def collect_bio(update: Update, context: CallbackContext) -> int:
    bio = update.message.text
    context.user_data['bio'] = bio
    update.message.reply_text('Registration info collected.')
    
    # Add a "Begin" button to start the onboarding process
    keyboard = [[InlineKeyboardButton("Begin", callback_data=BEGIN_ONBOARDING_CALLBACK_DATA)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Click "Begin" to start the onboarding process:', reply_markup=reply_markup)
    return ONBOARDING

def start_onboarding(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()

    context.user_data['video_index'] = 0
    return watch_video(update, context)


def watch_video(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()

    # Retrieve the current video index from user_data, or start with the first video
    video_index = context.user_data.get('video_index', 0)
    video_links = [
        "https://drive.google.com/file/d/1Gic00fJGSMGYdUxECLUkEVLy4k5Jjg3G/view?usp=sharing",
        "https://youtu.be/FkGK7bitav0?si=2-eYJBryZPEPSLGU",
        "https://youtube.com/shorts/6sUEsaaNMlc?si=3_ao53e-68tV8gNO"
    ]

    if video_index < len(video_links):
        # Send the video
        context.bot.send_message(chat_id=query.message.chat_id, text=f"Please watch this video: {video_links[video_index]}")
        
        # Proceed to the quiz question related to the video
        question, options, _ = quiz_questions[video_index]
        keyboard = [[InlineKeyboardButton(option, callback_data=option)] for option in options]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Send the quiz question with options as buttons
        context.bot.send_message(chat_id=query.message.chat_id, text=question, reply_markup=reply_markup)
        return QUIZ

def quiz(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()

    # Retrieve the current quiz question index
    question_index = context.user_data.get('video_index', 0)
    _, _, correct_answer = quiz_questions[question_index]

    # Check if the selected option is correct
    if query.data == correct_answer:
        # Correct answer, proceed to the next video/question
        context.user_data['video_index'] = question_index + 1
        # Check if there are more questions
        if context.user_data['video_index'] < len(quiz_questions):
            return watch_video(update, context)
        else:
            # No more questions, end conversation
            context.bot.send_message(chat_id=query.message.chat_id, text="Congratulations, you've completed the onboarding process!")
            return ConversationHandler.END
    else:
        # Incorrect answer, prompt to try again
        question, options, _ = quiz_questions[question_index]
        keyboard = [[InlineKeyboardButton(option, callback_data=option)] for option in options]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Resend the same quiz question with options as buttons
        query.edit_message_text(text="Incorrect, please try again.\n\n" + question, reply_markup=reply_markup)
        return QUIZ

def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('Onboarding has been canceled.')
    return ConversationHandler.END


# Define conversation handler for onboarding
conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
        EMAIL: [MessageHandler(Filters.text & ~Filters.command, collect_email)],
        PHONE: [MessageHandler(Filters.text & ~Filters.command, collect_phone)],
        BIO: [MessageHandler(Filters.text & ~Filters.command, collect_bio)],
        ONBOARDING: [CallbackQueryHandler(start_onboarding, pattern=BEGIN_ONBOARDING_CALLBACK_DATA)],
        WATCH_VIDEO: [CallbackQueryHandler(watch_video)],
        QUIZ: [CallbackQueryHandler(quiz)]
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)




def help(update, context):
    if not is_user_allowed(update, context):
        return
    help_text = ("List of commands:\n"
                 "/start - Initiate interaction with TheoBot\n"
                 "/help - Get a list of available commands\n"
                 "/register - Register a new user with the bot\n"
                 "/project - Add new project to Jira\n"
                 "/assignrole - Assign roles to users\n"
                 "/createtask - Create a new task within a project\n"
                 "/assigntask - Assign a task to a team member\n"
                 "/status - Check the status of a task\n"
                 "/calendar - View the Theometrics Calendar\n"
                 "/addevent - Add Event to the Theometrics Calendar\n"
                 "/rsvp - RSVP for calendar event\n"
                 "/settings - View or Edit Account Settings\n"
                 "/feedback - Provide feedback about the bot\n"
                 "More features coming soon!")
    update.message.reply_text(help_text)

def register(update, context):
    if not is_user_allowed(update, context):
        return
    keyboard = [
        [InlineKeyboardButton("Show me your Bevis", callback_data='show_bevis')],
        [InlineKeyboardButton("Create New Bevis", callback_data='create_bevis')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Please choose an option:', reply_markup=reply_markup)

def button(update, context):
    query = update.callback_query
    query.answer()
    if query.data == 'show_bevis':
        query.edit_message_text(text="Selected option: Show me your Bevis")
    elif query.data == 'create_bevis':
        query.edit_message_text(text="Selected option: Create New Bevis")


def assignrole(update, context):
    if not is_user_allowed(update, context):
        return
    update.message.reply_text('User role assignment is not yet implemented.')

def project(update, context):
    if not is_user_allowed(update, context):
        return
    update.message.reply_text('Creating a new project is not yet implemented.')

def createtask(update, context):
    if not is_user_allowed(update, context):
        return
    update.message.reply_text('Creating a new task is not yet implemented.')

def assigntask(update, context):
    if not is_user_allowed(update, context):
        return
    update.message.reply_text('Assigning a task is not yet implemented.')
    

def status(update, context):
    if not is_user_allowed(update, context):
        return
    update.message.reply_text('Checking task status is not yet implemented.')

def feedback(update, context):
    if not is_user_allowed(update, context):
        return
    update.message.reply_text('Feedback mechanism is not yet implemented.')

def calendar(update, context):
    if not is_user_allowed(update, context):
        return
    update.message.reply_text('Viewing the calendar is not yet implemented.')

def addevent(update, context):
    if not is_user_allowed(update, context):
        return
    update.message.reply_text('Submitting an event is not yet implemented.')

def rsvp(update, context):
    if not is_user_allowed(update, context):
        return
    update.message.reply_text('RSVP to an event is not yet implemented.')


def settings(update, context):
    if not is_user_allowed(update, context):
        return
    update.message.reply_text('Settings are not yet implemented.')

def feedback(update, context):
    if not is_user_allowed(update, context):
        return
    update.message.reply_text('Feedback functionality will be implemented.')

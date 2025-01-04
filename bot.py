import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters
from telegram.error import BadRequest

# Replace with your channel details
CHANNEL_USERNAME = "THE_REBEL_SQUAD"  # e.g., 'THE_REBEL_SQUAD'
CHANNEL_URL = f"https://t.me/{CHANNEL_USERNAME}"
CREATOR_NAME = "THE REBEL"  # Replace with your name or brand

# Check if the user is a member of the channel
def is_user_member(update):
    try:
        user_id = update.message.from_user.id
        member_status = update.message.bot.get_chat_member(CHANNEL_USERNAME, user_id).status
        return member_status in ["member", "administrator", "creator"]
    except BadRequest:
        return False  # User might not have interacted with the bot yet

# Command to start the bot
def start(update, context):
    # Force join message if the user isn't a member
    if not is_user_member(update):
        keyboard = [[InlineKeyboardButton("Join our Channel", url=CHANNEL_URL)]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(
            "You must join our channel to use this bot.", reply_markup=reply_markup
        )
        return

    # Main menu
    keyboard = [
        [InlineKeyboardButton("Menu", callback_data='menu')],
        [InlineKeyboardButton("About", callback_data='about')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Welcome to the bot! Use the buttons below.", reply_markup=reply_markup)

# Callback for the About button
def about(update, context):
    update.callback_query.answer()
    update.callback_query.edit_message_text(
        text=f"Bot created by {CREATOR_NAME}.\nJoin our channel here: {CHANNEL_URL}"
    )

# Menu for creating posts
def menu(update, context):
    update.callback_query.answer()
    keyboard = [
        [InlineKeyboardButton("Create Post with Button", callback_data='create_post')],
        [InlineKeyboardButton("Back", callback_data='back_to_main')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.callback_query.edit_message_text(
        text="Here is the menu. Choose an option:", reply_markup=reply_markup
    )

# Create post with button
def create_post(update, context):
    update.callback_query.answer()
    update.callback_query.edit_message_text(
        text="Send me the text for the post followed by the button text and URL.\n\nExample:\n`Post Text | Button Text | https://example.com`",
        parse_mode="Markdown",
    )
    context.user_data["awaiting_post"] = True

# Handle user message for post creation
def handle_message(update, context):
    if context.user_data.get("awaiting_post", False):
        try:
            post_text, button_text, button_url = map(str.strip, update.message.text.split("|"))
            keyboard = [[InlineKeyboardButton(button_text, url=button_url)]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            # Send post
            update.message.reply_text(post_text, reply_markup=reply_markup)
            update.message.reply_text("Your post has been created and sent!")
        except ValueError:
            update.message.reply_text(
                "Invalid format. Please use the format:\n`Post Text | Button Text | URL`",
                parse_mode="Markdown",
            )
        finally:
            context.user_data["awaiting_post"] = False

# Callback to go back to the main menu
def back_to_main(update, context):
    update.callback_query.answer()
    start(update.callback_query, context)

def main():
    # Fetch API token from environment variables
    API_TOKEN = os.getenv("API_TOKEN")  # Add your token as an environment variable

    updater = Updater(API_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Register command and callback handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CallbackQueryHandler(about, pattern='about'))
    dispatcher.add_handler(CallbackQueryHandler(menu, pattern='menu'))
    dispatcher.add_handler(CallbackQueryHandler(create_post, pattern='create_post'))
    dispatcher.add_handler(CallbackQueryHandler(back_to_main, pattern='back_to_main'))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    # Start the bot
    print("Bot is running...")
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()

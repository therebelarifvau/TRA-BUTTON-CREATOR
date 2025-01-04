from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext
import logging

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Admin Telegram IDs
ADMIN_IDS = [123456789, 987654321]  # Replace with admin Telegram user IDs

# Channel username
CHANNEL_USERNAME = "@YourChannelUsername"  # Replace with your channel username

# Start command
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        "Welcome to the Post Creator Bot! Use /createpost to create a post with buttons. "
        "Admins can share posts in the channel."
    )

# Create post command
def create_post(update: Update, context: CallbackContext) -> None:
    if len(context.args) < 1:
        update.message.reply_text("Please provide the post content. Example: /createpost Hello World!")
        return

    message = " ".join(context.args)
    keyboard = [
        [InlineKeyboardButton("Example Button 1", callback_data="btn1"),
         InlineKeyboardButton("Example Button 2", callback_data="btn2")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Save the post content in context for sharing
    context.user_data['post_message'] = message
    context.user_data['reply_markup'] = reply_markup

    update.message.reply_text(
        f"Preview of your post:\n\n{message}",
        reply_markup=reply_markup
    )
    update.message.reply_text(
        "Admins can use /sharepost to send this post to the channel."
    )

# Share post command (admin only)
def share_post(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        update.message.reply_text("Only admins can use this command.")
        return

    post_message = context.user_data.get('post_message')
    reply_markup = context.user_data.get('reply_markup')

    if not post_message or not reply_markup:
        update.message.reply_text("No post found to share. Use /createpost first.")
        return

    # Send to the channel
    context.bot.send_message(
        chat_id=CHANNEL_USERNAME,
        text=post_message,
        reply_markup=reply_markup
    )
    update.message.reply_text("Post successfully shared to the channel!")

# Button click callback
def button_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    query.edit_message_text(text=f"You clicked: {query.data}")

# Main function
def main() -> None:
    # Replace 'YOUR_API_TOKEN' with your bot token from BotFather
    updater = Updater("YOUR_API_TOKEN")

    dispatcher = updater.dispatcher

    # Handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("createpost", create_post))
    dispatcher.add_handler(CommandHandler("sharepost", share_post))
    dispatcher.add_handler(CallbackQueryHandler(button_callback))

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()

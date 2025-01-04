from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, CallbackContext
)
import requests

# Replace with your details
BOT_TOKEN = "8187684212:AAE5l3HB0w53NShfhxyruz28fMPLxpIv56s"
CHANNEL_USERNAME = "THE_REBEL_SQUAD"  # Replace with your channel username (without @)
BOT_NAME = "TRS BUTTON CREATOR"
YOUR_NAME = "ARIF ( THE REBEL )"
ADMIN_USER_ID = 6126538092  # Your Telegram ID (Admin)

# Check if the user is a member of the channel
def is_user_member(user_id: int) -> bool:
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getChatMember?chat_id=@{CHANNEL_USERNAME}&user_id={user_id}"
    response = requests.get(url).json()
    status = response.get("result", {}).get("status", "")
    return status in ["member", "administrator", "creator"]

# Start command handler
def start(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    if not is_user_member(user_id):
        keyboard = [
            [InlineKeyboardButton("Join Channel", url=f"https://t.me/{CHANNEL_USERNAME}")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(
            f"To use this bot, you must join our channel: @{CHANNEL_USERNAME}",
            reply_markup=reply_markup,
        )
    else:
        keyboard = [
            [InlineKeyboardButton("Create Post", callback_data="create_button")],
            [InlineKeyboardButton("About", callback_data="about")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text("Welcome! Use the buttons below:", reply_markup=reply_markup)

# Callback query handler
def button_handler(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    if query.data == "create_button":
        query.edit_message_text("Please send the post content (text, photo, or video).")
        context.user_data['awaiting_content'] = True
    elif query.data == "about":
        about_text = f"**Bot Name**: {BOT_NAME}\n**Your Name**: {YOUR_NAME}\n**Channel**: @{CHANNEL_USERNAME}"
        query.edit_message_text(about_text)

# Handle posts and create buttons
def handle_message(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    if not is_user_member(user_id):
        update.message.reply_text(
            f"To use this bot, you must join our channel: @{CHANNEL_USERNAME}"
        )
        return

    if context.user_data.get('awaiting_content'):
        context.user_data['post_content'] = update.message
        update.message.reply_text("Post received. Send the button label and URL in this format:\n`Label - URL`")
        context.user_data['awaiting_button'] = True
        context.user_data['awaiting_content'] = False
    elif context.user_data.get('awaiting_button'):
        button_data = update.message.text
        if " - " not in button_data:
            update.message.reply_text("Invalid format. Use this format: `Label - URL`")
            return

        label, url = button_data.split(" - ", 1)
        post_content = context.user_data.get('post_content')

        # Create inline keyboard
        keyboard = [[InlineKeyboardButton(label, url=url)]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Send post with button
        if post_content.text:
            update.message.reply_text(post_content.text, reply_markup=reply_markup)
        elif post_content.photo:
            update.message.reply_photo(post_content.photo[-1].file_id, caption=post_content.caption, reply_markup=reply_markup)
        elif post_content.video:
            update.message.reply_video(post_content.video.file_id, caption=post_content.caption, reply_markup=reply_markup)

        update.message.reply_text("Post created and ready to share!")
        context.user_data.clear()

# Admin-only Command to Share Post to Channel
def share_post(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    if user_id != ADMIN_USER_ID:
        update.message.reply_text("You are not authorized to share posts.")
        return

    if len(context.args) < 2:
        update.message.reply_text("Please provide the post content and the channel username.")
        return

    post_content = context.args[0]
    channel_username = context.args[1]

    try:
        context.bot.send_message(chat_id=f"@{channel_username}", text=post_content)
        update.message.reply_text(f"Post successfully shared to @{channel_username}.")
    except Exception as e:
        update.message.reply_text(f"Failed to share post: {e}")

# Main function to start the bot
def main() -> None:
    updater = Updater(BOT_TOKEN)

    # Add command handlers
    updater.dispatcher.add_handler(CommandHandler("start", start))
    updater.dispatcher.add_handler(CallbackQueryHandler(button_handler))
    updater.dispatcher.add_handler(MessageHandler(Filters.text | Filters.photo | Filters.video, handle_message))
    updater.dispatcher.add_handler(CommandHandler("share_post", share_post))

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()

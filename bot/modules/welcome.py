from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters

WELCOME_TEXT = "خوش اومدی به گروه 🌟\nلطفاً قوانین رو رعایت کن."

async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not msg.new_chat_members:
        return

    for member in msg.new_chat_members:
        await msg.reply_text(
            f"{member.mention_html()} \n{WELCOME_TEXT}",
            parse_mode="HTML",
        )

def get_welcome_handlers():
    return [
        MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_member),
    ]


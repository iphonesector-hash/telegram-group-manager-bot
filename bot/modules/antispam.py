from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters
import time

user_messages = {}
MAX_MSG_PER_10S = 5

async def antispam_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    user_id = msg.from_user.id
    now = time.time()

    if user_id not in user_messages:
        user_messages[user_id] = []

    user_messages[user_id] = [t for t in user_messages[user_id] if now - t < 10]
    user_messages[user_id].append(now)

    if len(user_messages[user_id]) > MAX_MSG_PER_10S:
        try:
            await msg.delete()
        except:
            pass

def get_antispam_handlers():
    return [
        MessageHandler(filters.ALL, antispam_filter),
    ]


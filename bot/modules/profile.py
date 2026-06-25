from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters

users = {}

def ensure_user(user_id):
    if user_id not in users:
        users[user_id] = {
            "messages": 0,
            "coins": 0,
        }

async def count_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    user_id = msg.from_user.id
    ensure_user(user_id)
    users[user_id]["messages"] += 1
    users[user_id]["coins"] += 1

async def profile_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    user_id = user.id
    ensure_user(user_id)

    data = users[user_id]
    text = (
        f"👤 پروفایل {user.full_name}\n"
        f"📨 تعداد پیام‌ها: {data['messages']}\n"
        f"🪙 سکه‌ها: {data['coins']}\n"
    )
    await update.message.reply_text(text)

async def top_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not users:
        await update.message.reply_text("هنوز کسی امتیاز نگرفته.")
        return

    sorted_users = sorted(users.items(), key=lambda x: x[1]["coins"], reverse=True)[:10]
    lines = []
    for i, (uid, data) in enumerate(sorted_users, start=1):
        lines.append(f"{i}. {uid} — 🪙 {data['coins']}")

    await update.message.reply_text("🏆 برترین‌ها:\n" + "\n".join(lines))

def get_profile_handlers():
    return [
        MessageHandler(filters.ALL, count_message),
        CommandHandler("profile", profile_cmd),
        CommandHandler("top", top_cmd),
    ]

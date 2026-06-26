import os
import datetime
import re
from telegram import Update
from telegram.ext import ContextTypes
from bot.database.session import get_session
from bot.database.models import Group

# Commander / Owner Identity
OWNER_ID = 5382025178  # Recognized as "فرمانده پیمان"
OWNER_NAME = "فرمانده پیمان"

async def is_owner(user_id):
    return user_id == OWNER_ID

async def is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user:
        return False

    # Owner always has admin permissions
    if update.effective_user.id == OWNER_ID:
        return True

    if not update.effective_chat or update.effective_chat.type == "private":
        return True

    try:
        member = await context.bot.get_chat_member(update.effective_chat.id, update.effective_user.id)
        return member.status in ["administrator", "creator"]
    except:
        return False

def get_group(session, chat_id, title=None):
    group = session.query(Group).filter(Group.id == chat_id).first()
    if not group:
        group = Group(id=chat_id, title=title or f"Group {chat_id}")
        session.add(group)
        session.commit()
    return group

async def get_reply_text(user, text):
    """Returns a respectful reply for the owner or styled text for others."""
    if user.id == OWNER_ID:
        return f"🫡 **فرمانده پیمان** عزیز، در خدمت شما هستم:\n\n{text}"

    # Rank badges for other users based on level or stats could go here
    return text

def get_user_badge(user_db):
    if user_db.id == OWNER_ID:
        return "👑 فرمانده پیمان"
    if user_db.level >= 20:
        return "👑 Legend"
    if user_db.level >= 10:
        return "🥇 Gold"
    if user_db.level >= 5:
        return "🥈 Silver"
    return "🥉 Bronze"

async def get_user_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Extracts user_id and name from message reply or command arguments.
    Returns: (user_id, name) or (None, None)
    """
    if update.effective_message.reply_to_message:
        user = update.effective_message.reply_to_message.from_user
        return user.id, user.first_name

    if context.args:
        arg = context.args[0]
        if arg.isdigit():
            user_id = int(arg)
            # Try to get member info to have a name, otherwise fallback to ID
            try:
                member = await context.bot.get_chat_member(update.effective_chat.id, user_id)
                return user_id, member.user.first_name
            except:
                return user_id, f"User {user_id}"

    return None, None

def parse_time(time_str):
    """
    Parses strings like '60', '1h', '2d' into timedelta.
    Default unit is minutes if only number is provided.
    """
    if not time_str:
        return None

    try:
        if time_str.isdigit():
            return datetime.timedelta(minutes=int(time_str))

        match = re.match(r"^(\d+)([smhd])$", time_str.lower())
        if not match:
            return None

        amount, unit = match.groups()
        amount = int(amount)

        if unit == "s":
            return datetime.timedelta(seconds=amount)
        elif unit == "m":
            return datetime.timedelta(minutes=amount)
        elif unit == "h":
            return datetime.timedelta(hours=amount)
        elif unit == "d":
            return datetime.timedelta(days=amount)
    except:
        pass

    return None

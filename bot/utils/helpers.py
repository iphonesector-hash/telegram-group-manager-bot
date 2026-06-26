import os
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
    """Returns a respectful reply for the owner if applicable."""
    if user.id == OWNER_ID:
        return f"🫡 **{OWNER_NAME}** عزیز، در خدمت شما هستم:\n\n{text}"
    return text

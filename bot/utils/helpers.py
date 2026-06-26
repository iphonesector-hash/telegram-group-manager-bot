from telegram import Update
from telegram.ext import ContextTypes
from bot.database.session import get_session
from bot.database.models import Group

async def is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

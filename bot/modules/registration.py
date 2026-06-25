from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters
from bot.database.session import get_session
from bot.database.models import User, Group

async def register_user_and_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user:
        return

    session = get_session()
    user_id = update.effective_user.id

    # Register User
    user = session.query(User).filter(User.id == user_id).first()
    if not user:
        user = User(
            id=user_id,
            username=update.effective_user.username,
            first_name=update.effective_user.first_name,
            coins=10,  # Welcome bonus
            xp=0,
            level=1,
            message_count=0
        )
        session.add(user)
    else:
        # Update name/username if changed
        user.username = update.effective_user.username
        user.first_name = update.effective_user.first_name

    # Register Group (if message is from a group)
    if update.effective_chat and update.effective_chat.type in ["group", "supergroup"]:
        chat_id = update.effective_chat.id
        group = session.query(Group).filter(Group.id == chat_id).first()
        if not group:
            group = Group(
                id=chat_id,
                title=update.effective_chat.title
            )
            session.add(group)
        else:
            group.title = update.effective_chat.title

    try:
        session.commit()
    except Exception as e:
        print(f"❌ Error during registration: {e}")
        session.rollback()
    finally:
        session.close()

def get_registration_handlers():
    # MessageHandler in a high priority group
    return [
        MessageHandler(filters.ALL, register_user_and_group)
    ]

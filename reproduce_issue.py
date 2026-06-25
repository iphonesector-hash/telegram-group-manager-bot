import asyncio
from unittest.mock import MagicMock, AsyncMock
from telegram import Update, User as TGUser, Message, Chat
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import sys
import os

# Set up paths
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from bot.database.session import init_db, get_session
from bot.database.models import User as DBUser
from bot.modules.profile import profile_cmd, top_cmd

async def test_profile_cmd():
    init_db()

    # Mock Update
    user = TGUser(id=12345, first_name="Test", is_bot=False, username="testuser")
    chat = Chat(id=12345, type="private")
    message = Message(message_id=1, date=None, chat=chat, from_user=user, text="/profile")
    update = Update(update_id=1, message=message)

    # Mock Context
    context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)

    # Mock reply_text
    message.reply_text = AsyncMock()

    # Manually register user in DB for test
    session = get_session()
    db_user = DBUser(id=12345, first_name="Test", coins=100)
    session.merge(db_user)
    session.commit()
    session.close()

    # Call handler
    await profile_cmd(update, context)

    # Check if reply_text was called
    if message.reply_text.called:
        print("✅ profile_cmd replied successfully.")
        print(f"Reply text: {message.reply_text.call_args[0][0]}")
    else:
        print("❌ profile_cmd did not reply.")

if __name__ == "__main__":
    asyncio.run(test_profile_cmd())

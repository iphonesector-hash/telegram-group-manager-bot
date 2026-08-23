import asyncio
import logging
import os

from telegram import Update
from telegram.ext import CommandHandler, TypeHandler

from bot.services.release_publisher import maybe_publish_current_release

LOGGER = logging.getLogger(__name__)
OWNER_ID = int(os.getenv("OWNER_ID", "5147526780"))
_checked_release = False
_lock = asyncio.Lock()


async def force_release_announcement(update, context):
    """Owner QA command: publish the current release immediately."""
    global _checked_release
    user = update.effective_user
    message = update.effective_message
    if not user or not message or int(user.id) != OWNER_ID:
        return
    result = await maybe_publish_current_release(context.bot, force=True)
    if result.get("ok"):
        _checked_release = True
        mode = "متنی" if result.get("fallback_text") else "تصویری"
        await message.reply_text("✅ Release سکتور کوچولو منتشر شد.\nحالت انتشار: " + mode)
    else:
        await message.reply_text("❌ انتشار Release انجام نشد: " + str(result.get("error") or result.get("reason") or "unknown")[:180])


async def release_announcement_handler(update, context):
    """Publish the current Sector release once, then let the update continue.

    The database-backed publisher is the source of truth. The process-local flag
    only avoids a database read on every Telegram update within the same warm
    Vercel instance.
    """
    global _checked_release
    if _checked_release:
        return

    async with _lock:
        if _checked_release:
            return
        try:
            result = await maybe_publish_current_release(context.bot)
            if result.get("ok"):
                _checked_release = True
            else:
                LOGGER.warning("Release announcement not published yet: %s", result)
        except Exception as exc:
            LOGGER.warning("Release announcement check failed: %s", exc)


def get_handlers():
    # Command first: PTB runs at most one matching handler per group/update.
    return [
        CommandHandler("sectorrelease", force_release_announcement),
        TypeHandler(Update, release_announcement_handler),
    ]

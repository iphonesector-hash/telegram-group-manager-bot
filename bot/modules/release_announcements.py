import asyncio
import logging

from telegram import Update
from telegram.ext import TypeHandler

from bot.services.release_publisher import maybe_publish_current_release

LOGGER = logging.getLogger(__name__)
_checked_release = False
_lock = asyncio.Lock()


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
    return [TypeHandler(Update, release_announcement_handler)]

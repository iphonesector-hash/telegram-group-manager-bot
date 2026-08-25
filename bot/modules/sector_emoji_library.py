"""Owner-only management for the official Sector Premium emoji library."""
import os

from telegram import Update
from telegram.ext import ApplicationHandlerStop, CommandHandler, ContextTypes

from bot.database.models import AppSetting
from bot.database.session import get_session
from bot.utils.animated_emoji import get_sector_emoji_ids, invalidate_sector_emoji_cache


def _owner_id():
    try:
        return int(os.getenv("OWNER_ID") or "0")
    except ValueError:
        return 0


async def reset_sector_emojis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or int(update.effective_user.id) != _owner_id():
        raise ApplicationHandlerStop()
    session = get_session()
    try:
        row = session.query(AppSetting).filter(AppSetting.key == "sector_custom_emoji_id").first()
        if row:
            row.value = []
        else:
            session.add(AppSetting(key="sector_custom_emoji_id", value=[]))
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
    invalidate_sector_emoji_cache()
    await update.effective_message.reply_text(
        "کتابخانه ایموجی‌های پرمیوم سکتور پاک شد. حالا فقط ایموجی‌های دلخواهت را در همین چت خصوصی بفرست؛ سکتور آن‌ها را به مجموعه رسمی اضافه می‌کند."
    )
    raise ApplicationHandlerStop()


async def sector_emoji_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or int(update.effective_user.id) != _owner_id():
        raise ApplicationHandlerStop()
    ids = get_sector_emoji_ids(force=True)
    await update.effective_message.reply_text(
        f"کتابخانه پرمیوم سکتور: {len(ids)} ایموجی فعال.\n"
        "برای ساخت یک مجموعه کاملاً جدید اول /resetsectoremoji را بزن و بعد فقط ایموجی‌های موردنظر را بفرست."
    )
    raise ApplicationHandlerStop()


def get_handlers():
    return [
        CommandHandler("resetsectoremoji", reset_sector_emojis),
        CommandHandler("sectoremojis", sector_emoji_status),
    ]

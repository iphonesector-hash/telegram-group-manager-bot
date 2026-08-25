"""Owner-only append-only management for Sector Koochooloo Premium emojis.

This library is isolated from the bot-wide legacy emoji setting; it only adds
new Sector Koochooloo emoji IDs and never clears or rewrites the old library.
"""
import os

from telegram import Update
from telegram.ext import ApplicationHandlerStop, CommandHandler, ContextTypes, MessageHandler, filters

from bot.database.models import AppSetting
from bot.database.session import get_session
from bot.utils.animated_emoji import (
    SECTOR_KOOCHOOLOO_EMOJI_KEY,
    get_sector_emoji_ids,
    invalidate_sector_emoji_cache,
)


def _owner_id():
    try:
        return int(os.getenv("OWNER_ID") or "5147526780")
    except ValueError:
        return 5147526780


def _extract_custom_ids(message):
    entities = list(getattr(message, "entities", None) or []) + list(getattr(message, "caption_entities", None) or [])
    return [str(e.custom_emoji_id) for e in entities if str(getattr(e, "type", "")) == "custom_emoji" and getattr(e, "custom_emoji_id", None)]


def _append_ids(custom_ids):
    session = get_session()
    try:
        row = session.query(AppSetting).filter(AppSetting.key == SECTOR_KOOCHOOLOO_EMOJI_KEY).first()
        existing = row.value if row and isinstance(row.value, list) else ([row.value] if row and row.value else [])
        merged = list(dict.fromkeys([str(x) for x in existing + list(custom_ids) if str(x).isdigit()]))[:32]
        if row:
            row.value = merged
        else:
            session.add(AppSetting(key=SECTOR_KOOCHOOLOO_EMOJI_KEY, value=merged))
        session.commit()
        return len(merged)
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


async def add_sector_emojis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or int(update.effective_user.id) != _owner_id():
        raise ApplicationHandlerStop()
    source = update.effective_message.reply_to_message or update.effective_message
    custom_ids = _extract_custom_ids(source)
    if not custom_ids:
        await update.effective_message.reply_text(
            "ایموجی‌های پرمیوم موردنظر سکتور کوچولو را بفرست؛ یا روی پیامشان ریپلای کن و /setsectoremoji را بزن."
        )
        raise ApplicationHandlerStop()
    total = _append_ids(custom_ids)
    invalidate_sector_emoji_cache()
    await update.effective_message.reply_text(
        f"✅ {len(custom_ids)} ایموجی به کتابخانه اختصاصی سکتور کوچولو اضافه شد. مجموع فعلی: {total}"
    )
    raise ApplicationHandlerStop()


async def capture_sector_emojis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """In the owner's private chat, simply sending custom emojis appends them."""
    if not update.effective_chat or update.effective_chat.type != "private":
        return
    await add_sector_emojis(update, context)


async def sector_emoji_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or int(update.effective_user.id) != _owner_id():
        raise ApplicationHandlerStop()
    ids = get_sector_emoji_ids(force=True)
    session = get_session()
    try:
        row = session.query(AppSetting).filter(AppSetting.key == SECTOR_KOOCHOOLOO_EMOJI_KEY).first()
        dedicated = row.value if row and isinstance(row.value, list) else ([row.value] if row and row.value else [])
        dedicated_count = len([x for x in dedicated if str(x).isdigit()])
    finally:
        session.close()
    suffix = "" if dedicated_count else "\nهنوز کتابخانه اختصاصی خالی است؛ فعلاً fallback قدیمی نمایش داده می‌شود."
    await update.effective_message.reply_text(
        f"کتابخانه اختصاصی سکتور کوچولو: {dedicated_count} ایموجی.\nایموجی فعال فعلی: {len(ids)} مورد.{suffix}"
    )
    raise ApplicationHandlerStop()


def get_handlers():
    owner = filters.User(_owner_id())
    return [
        CommandHandler("setsectoremoji", add_sector_emojis),
        CommandHandler("sectoremojis", sector_emoji_status),
        MessageHandler(owner & filters.Entity("custom_emoji"), capture_sector_emojis),
    ]

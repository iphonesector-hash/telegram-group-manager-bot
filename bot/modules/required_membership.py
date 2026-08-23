import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ChatMemberStatus, ChatType
from telegram.ext import CallbackQueryHandler, MessageHandler, filters, ApplicationHandlerStop

REQUIRED_CHAT = os.getenv("REQUIRED_MEMBERSHIP_CHAT", "@sectorland")
REQUIRED_CHAT_URL = os.getenv("REQUIRED_MEMBERSHIP_URL", "https://t.me/sectorland")
VERIFY_CALLBACK = "sectorland:verify-membership"


def _join_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📣 عضویت در SectorLand", url=REQUIRED_CHAT_URL)],
        [InlineKeyboardButton("✅ عضو شدم — بررسی کن", callback_data=VERIFY_CALLBACK)],
    ])


async def is_required_member(bot, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(REQUIRED_CHAT, user_id)
        if member.status in {ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.MEMBER}:
            return True
        if member.status == ChatMemberStatus.RESTRICTED:
            return bool(getattr(member, "is_member", False))
        return False
    except Exception as exc:
        # Fail open on Telegram/API outages so an external error never locks all users out.
        print(f"⚠️ Required-membership check failed: {exc}")
        return True


async def membership_gate(update: Update, context):
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    if not message or not user or not chat or user.is_bot:
        return
    # Forced subscription is only for people using the bot privately; group moderation must keep working.
    if chat.type != ChatType.PRIVATE:
        return
    if await is_required_member(context.bot, user.id):
        return
    await message.reply_text(
        "🔒 برای استفاده از ربات و مینی‌اپ SectorLand ابتدا باید عضو کانال اصلی SectorLand باشی.\n\n"
        "بعد از عضویت روی «عضو شدم — بررسی کن» بزن تا دسترسی‌ات همان لحظه فعال شود.",
        reply_markup=_join_keyboard(),
    )
    raise ApplicationHandlerStop


async def verify_membership(update: Update, context):
    query = update.callback_query
    if not query or not query.from_user:
        return
    await query.answer()
    if await is_required_member(context.bot, query.from_user.id):
        await query.edit_message_text("✅ عضویت تأیید شد. حالا می‌تونی از همه امکانات SectorLand استفاده کنی.\n\n/start")
        return
    await query.answer("هنوز عضویتت در @sectorland تأیید نشده.", show_alert=True)


def get_handlers():
    return [
        CallbackQueryHandler(verify_membership, pattern=f"^{VERIFY_CALLBACK}$"),
        MessageHandler(filters.ALL, membership_gate),
    ]

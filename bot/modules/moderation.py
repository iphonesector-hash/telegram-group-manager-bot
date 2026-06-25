import re
import datetime
from telegram import Update, ChatPermissions
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters
from bot.database.session import get_session
from bot.database.models import User, Group, Warning, Mute

def parse_time(time_str):
    if not time_str:
        return None
    match = re.match(r"(\d+)([smhd])", time_str.lower())
    if not match:
        return None
    val, unit = match.groups()
    val = int(val)
    if unit == 's':
        return datetime.timedelta(seconds=val)
    elif unit == 'm':
        return datetime.timedelta(minutes=val)
    elif unit == 'h':
        return datetime.timedelta(hours=val)
    elif unit == 'd':
        return datetime.timedelta(days=val)
    return None

async def is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == "private":
        return True

    # Check if user is an admin in the group
    member = await context.bot.get_chat_member(update.effective_chat.id, update.effective_user.id)
    return member.status in ["administrator", "creator"]

async def get_user_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        return update.message.reply_to_message.from_user.id, update.message.reply_to_message.from_user.full_name

    if context.args:
        arg = context.args[0]
        if arg.isdigit():
            return int(arg), f"User {arg}"
        if arg.startswith('@'):
            session = get_session()
            user = session.query(User).filter(User.username == arg[1:]).first()
            session.close()
            if user:
                return user.id, user.first_name
    return None, None

async def warn_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat or update.effective_chat.type == "private":
        return

    if not await is_admin(update, context):
        await update.message.reply_text("❌ شما دسترسی لازم برای این کار را ندارید.")
        return

    user_id, name = await get_user_id(update, context)
    if not user_id:
        await update.message.reply_text("❌ کاربر مورد نظر یافت نشد. ریپلای کنید یا آیدی عددی/یوزرنیم بزنید.")
        return

    # Check if target is admin
    target_member = await context.bot.get_chat_member(update.effective_chat.id, user_id)
    if target_member.status in ["administrator", "creator"]:
        await update.message.reply_text("❌ شما نمی‌توانید ادمین را اخطار دهید.")
        return

    reason = "بدون دلیل"
    if len(context.args) > 1:
        reason = " ".join(context.args[1:])

    session = get_session()
    new_warn = Warning(
        user_id=user_id,
        group_id=update.effective_chat.id,
        reason=reason,
        warned_by=update.effective_user.id
    )
    session.add(new_warn)

    warn_count = session.query(Warning).filter(
        Warning.user_id == user_id,
        Warning.group_id == update.effective_chat.id
    ).count()

    session.commit()
    await update.message.reply_text(f"⚠️ کاربر {name} اخطار دریافت کرد.\nتعداد اخطارها: {warn_count}\nدلیل: {reason}")

    if warn_count >= 3:
        await update.message.reply_text("🚨 تعداد اخطارها به حد مجاز (۳) رسید. کاربر اخراج می‌شود.")
        try:
            await update.effective_chat.ban_member(user_id)
        except Exception as e:
            await update.message.reply_text(f"❌ خطا در اخراج: {e}")

    session.close()

async def warns_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id, name = await get_user_id(update, context)
    if not user_id:
        user_id, name = update.effective_user.id, update.effective_user.first_name

    session = get_session()
    warns = session.query(Warning).filter(
        Warning.user_id == user_id,
        Warning.group_id == update.effective_chat.id
    ).all()

    if not warns:
        await update.message.reply_text(f"✅ کاربر {name} هیچ اخطاری ندارد.")
    else:
        text = f"📋 لیست اخطارهای {name}:\n"
        for i, w in enumerate(warns, 1):
            text += f"{i}. {w.reason} ({w.created_at.strftime('%Y-%m-%d')})\n"
        await update.message.reply_text(text)
    session.close()

async def clearwarn_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        await update.message.reply_text("❌ شما دسترسی لازم برای این کار را ندارید.")
        return

    user_id, name = await get_user_id(update, context)
    if not user_id:
        await update.message.reply_text("❌ کاربر یافت نشد.")
        return

    session = get_session()
    session.query(Warning).filter(
        Warning.user_id == user_id,
        Warning.group_id == update.effective_chat.id
    ).delete()
    session.commit()
    session.close()
    await update.message.reply_text(f"✅ تمام اخطارهای {name} پاک شد.")

async def mute_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        await update.message.reply_text("❌ شما دسترسی لازم برای این کار را ندارید.")
        return

    user_id, name = await get_user_id(update, context)
    if not user_id:
        await update.message.reply_text("❌ کاربر یافت نشد.")
        return

    # Check if target is admin
    target_member = await context.bot.get_chat_member(update.effective_chat.id, user_id)
    if target_member.status in ["administrator", "creator"]:
        await update.message.reply_text("❌ شما نمی‌توانید ادمین را بی‌صدا کنید.")
        return

    duration_str = context.args[1] if len(context.args) > 1 else "1h"
    delta = parse_time(duration_str)
    if not delta:
        await update.message.reply_text("❌ زمان نامعتبر است (مثال: 10m, 1h, 1d)")
        return

    until = datetime.datetime.now(datetime.UTC).replace(tzinfo=None) + delta

    session = get_session()
    mute = session.query(Mute).filter(Mute.user_id == user_id, Mute.group_id == update.effective_chat.id).first()
    if not mute:
        mute = Mute(user_id=user_id, group_id=update.effective_chat.id, until=until)
        session.add(mute)
    else:
        mute.until = until
    session.commit()
    session.close()

    try:
        await update.effective_chat.restrict_member(user_id, ChatPermissions(can_send_messages=False), until_date=until)
        await update.message.reply_text(f"🔇 کاربر {name} تا {duration_str} دیگر بی‌صدا شد.")
    except Exception as e:
        await update.message.reply_text(f"❌ خطا در محدودسازی (ربات باید ادمین باشد): {e}")

async def unmute_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        await update.message.reply_text("❌ شما دسترسی لازم برای این کار را ندارید.")
        return

    user_id, name = await get_user_id(update, context)
    if not user_id:
        await update.message.reply_text("❌ کاربر یافت نشد.")
        return

    session = get_session()
    session.query(Mute).filter(Mute.user_id == user_id, Mute.group_id == update.effective_chat.id).delete()
    session.commit()
    session.close()

    try:
        await update.effective_chat.restrict_member(user_id, ChatPermissions(
            can_send_messages=True,
            can_send_polls=True,
            can_send_other_messages=True,
            can_add_web_page_previews=True
        ))
        await update.message.reply_text(f"🔊 کاربر {name} آزاد شد.")
    except Exception as e:
        await update.message.reply_text(f"❌ خطا: {e}")

async def ban_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        await update.message.reply_text("❌ شما دسترسی لازم برای این کار را ندارید.")
        return

    user_id, name = await get_user_id(update, context)
    if not user_id:
        await update.message.reply_text("❌ کاربر یافت نشد.")
        return

    # Check if target is admin
    target_member = await context.bot.get_chat_member(update.effective_chat.id, user_id)
    if target_member.status in ["administrator", "creator"]:
        await update.message.reply_text("❌ شما نمی‌توانید ادمین را اخراج کنید.")
        return

    try:
        await update.effective_chat.ban_member(user_id)
        await update.message.reply_text(f"🚫 کاربر {name} از گروه اخراج و مسدود شد.")
    except Exception as e:
        await update.message.reply_text(f"❌ خطا: {e}")

async def unban_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        await update.message.reply_text("❌ شما دسترسی لازم برای این کار را ندارید.")
        return

    if not context.args:
        await update.message.reply_text("❌ لطفا آیدی عددی کاربر را وارد کنید.")
        return

    user_id_str = context.args[0]
    if not user_id_str.isdigit():
        await update.message.reply_text("❌ آیدی عددی نامعتبر است.")
        return

    user_id = int(user_id_str)
    try:
        await update.effective_chat.unban_member(user_id)
        await update.message.reply_text(f"✅ کاربر {user_id} از لیست سیاه خارج شد.")
    except Exception as e:
        await update.message.reply_text(f"❌ خطا: {e}")

async def mute_checker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not update.effective_chat:
        return

    session = get_session()
    mute = session.query(Mute).filter(
        Mute.user_id == update.effective_user.id,
        Mute.group_id == update.effective_chat.id
    ).first()

    if mute:
        now = datetime.datetime.now(datetime.UTC).replace(tzinfo=None)
        if mute.until > now:
            try:
                await update.message.delete()
            except:
                pass
        else:
            session.delete(mute)
            session.commit()
    session.close()

def get_moderation_handlers():
    return [
        CommandHandler("warn", warn_cmd),
        CommandHandler("warns", warns_cmd),
        CommandHandler("clearwarn", clearwarn_cmd),
        CommandHandler("mute", mute_cmd),
        CommandHandler("unmute", unmute_cmd),
        CommandHandler("ban", ban_cmd),
        CommandHandler("unban", unban_cmd),
        MessageHandler(filters.ALL & ~filters.COMMAND, mute_checker),
    ]

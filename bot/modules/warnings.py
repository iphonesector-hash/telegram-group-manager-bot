import re
import datetime
from telegram import Update, ChatPermissions
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters, ApplicationHandlerStop
from bot.database.session import get_session
from bot.database.models import User, Group, Warning, Mute
from bot.utils.helpers import is_admin, get_group
from bot.utils.keyboards import (
    get_warnings_mgmt_menu, get_mutes_mgmt_menu, get_bans_mgmt_menu,
    get_user_info_mgmt_menu, get_security_mgmt_menu, get_member_mgmt_menu
)

def parse_time(time_str):
    if not time_str:
        return None
    if time_str.isdigit():
        return datetime.timedelta(minutes=int(time_str))

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

async def get_user_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        return update.message.reply_to_message.from_user.id, update.message.reply_to_message.from_user.full_name

    if context.args:
        arg = context.args[0]
        if arg.isdigit():
            return int(arg), f"کاربر {arg}"
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
        await update.effective_message.reply_text("❌ شما دسترسی لازم برای این کار را ندارید.")
        return

    user_id, name = await get_user_id(update, context)
    if not user_id:
        await update.effective_message.reply_text("❌ کاربر مورد نظر یافت نشد. ریپلای کنید یا آیدی عددی/یوزرنیم بزنید.")
        return

    try:
        target_member = await context.bot.get_chat_member(update.effective_chat.id, user_id)
        if target_member.status in ["administrator", "creator"]:
            await update.effective_message.reply_text("❌ شما نمی‌توانید ادمین را اخطار دهید.")
            return
    except:
        pass

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
    await update.effective_message.reply_text(f"⚠️ کاربر {name} اخطار دریافت کرد.\nتعداد اخطارها: {warn_count}\nدلیل: {reason}")

    if warn_count >= 3:
        await update.effective_message.reply_text("🚨 تعداد اخطارها به حد مجاز (۳) رسید. کاربر اخراج می‌شود.")
        try:
            await update.effective_chat.ban_member(user_id)
        except Exception as e:
            await update.effective_message.reply_text(f"❌ خطا در اخراج: {e}")

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
        await update.effective_message.reply_text(f"✅ کاربر {name} هیچ اخطاری ندارد.")
    else:
        text = f"📋 لیست اخطارهای {name}:\n"
        for i, w in enumerate(warns, 1):
            text += f"{i}. {w.reason} ({w.created_at.strftime('%Y-%m-%d')})\n"
        await update.effective_message.reply_text(text)
    session.close()

async def clearwarn_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        await update.effective_message.reply_text("❌ شما دسترسی لازم برای این کار را ندارید.")
        return

    user_id, name = await get_user_id(update, context)
    if not user_id:
        await update.effective_message.reply_text("❌ کاربر یافت نشد.")
        return

    session = get_session()
    session.query(Warning).filter(
        Warning.user_id == user_id,
        Warning.group_id == update.effective_chat.id
    ).delete()
    session.commit()
    session.close()
    await update.effective_message.reply_text(f"✅ تمام اخطارهای {name} پاک شد.")

async def mute_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        await update.effective_message.reply_text("❌ شما دسترسی لازم برای این کار را ندارید.")
        return

    user_id, name = await get_user_id(update, context)
    if not user_id:
        await update.effective_message.reply_text("❌ کاربر یافت نشد.")
        return

    try:
        target_member = await context.bot.get_chat_member(update.effective_chat.id, user_id)
        if target_member.status in ["administrator", "creator"]:
            await update.effective_message.reply_text("❌ شما نمی‌توانید ادمین را بی‌صدا کنید.")
            return
    except:
        pass

    duration_str = context.args[1] if len(context.args) > 1 else "60"
    delta = parse_time(duration_str)
    if not delta:
        await update.effective_message.reply_text("❌ زمان نامعتبر است (مثال: 60 یا 1h)")
        return

    until = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None) + delta

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
        await update.effective_message.reply_text(f"🔇 کاربر {name} تا {duration_str} دقیقه دیگر بی‌صدا شد.")
    except Exception as e:
        await update.effective_message.reply_text(f"❌ خطا در محدودسازی: {e}")

async def unmute_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        await update.effective_message.reply_text("❌ شما دسترسی لازم برای این کار را ندارید.")
        return

    user_id, name = await get_user_id(update, context)
    if not user_id:
        await update.effective_message.reply_text("❌ کاربر یافت نشد.")
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
        await update.effective_message.reply_text(f"🔊 کاربر {name} آزاد شد.")
    except Exception as e:
        await update.effective_message.reply_text(f"❌ خطا: {e}")

async def ban_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        await update.effective_message.reply_text("❌ شما دسترسی لازم برای این کار را ندارید.")
        return

    user_id, name = await get_user_id(update, context)
    if not user_id:
        await update.effective_message.reply_text("❌ کاربر یافت نشد.")
        return

    try:
        target_member = await context.bot.get_chat_member(update.effective_chat.id, user_id)
        if target_member.status in ["administrator", "creator"]:
            await update.effective_message.reply_text("❌ شما نمی‌توانید ادمین را اخراج کنید.")
            return
    except:
        pass

    try:
        await update.effective_chat.ban_member(user_id)
        await update.effective_message.reply_text(f"🚫 کاربر {name} از گروه اخراج و مسدود شد.")
    except Exception as e:
        await update.effective_message.reply_text(f"❌ خطا: {e}")

async def unban_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        await update.effective_message.reply_text("❌ شما دسترسی لازم برای این کار را ندارید.")
        return

    if not context.args:
        await update.effective_message.reply_text("❌ لطفا آیدی عددی کاربر را وارد کنید.")
        return

    user_id_str = context.args[0]
    if not user_id_str.isdigit():
        await update.effective_message.reply_text("❌ آیدی عددی نامعتبر است.")
        return

    user_id = int(user_id_str)
    try:
        await update.effective_chat.unban_member(user_id)
        await update.effective_message.reply_text(f"✅ کاربر {user_id} از لیست سیاه خارج شد.")
    except Exception as e:
        await update.effective_message.reply_text(f"❌ خطا: {e}")

async def mute_checker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not update.effective_chat:
        return

    if await is_admin(update, context):
        return

    session = get_session()
    mute = session.query(Mute).filter(
        Mute.user_id == update.effective_user.id,
        Mute.group_id == update.effective_chat.id
    ).first()

    if mute:
        now = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
        if mute.until > now:
            try:
                await update.effective_message.delete()
                session.close()
                raise ApplicationHandlerStop()
            except ApplicationHandlerStop:
                raise
            except:
                pass
        else:
            session.delete(mute)
            session.commit()
    session.close()

async def member_mgmt_buttons_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context): return
    text = update.message.text

    if text == "⚠️ اخطارها":
        await update.effective_message.reply_text("⚠️ مدیریت اخطارهای کاربران:", reply_markup=get_warnings_mgmt_menu())
    elif text == "➕ اخطار کاربر":
        await update.effective_message.reply_text("💡 برای اخطار دادن، روی پیام کاربر ریپلای کنید و دستور /warn را بزنید.")
    elif text == "📋 لیست اخطارها":
        await update.effective_message.reply_text("💡 برای دیدن لیست اخطارها، روی کاربر ریپلای کنید و دستور /warns را بزنید.")
    elif text == "🗑 حذف آخرین اخطار":
        await update.effective_message.reply_text("💡 این قابلیت بزودی اضافه می‌شود. فعلاً از /clearwarn استفاده کنید.")
    elif text == "🔄 پاک کردن همه اخطارها":
        await update.effective_message.reply_text("💡 برای پاک کردن همه اخطارها، روی کاربر ریپلای کنید و دستور /clearwarn را بزنید.")

    elif text == "🔇 محدودیت‌ها":
        await update.effective_message.reply_text("🔇 مدیریت محدودیت‌های چت:", reply_markup=get_mutes_mgmt_menu())
    elif text == "🔇 سکوت کاربر":
        await update.effective_message.reply_text("💡 روی کاربر ریپلای کنید و دستور /mute را بزنید.")
    elif text == "⏱ سکوت زمان‌دار":
        await update.effective_message.reply_text("💡 روی کاربر ریپلای کنید و بنویسید: /mute 1h (یا هر زمان دیگری).")
    elif text == "🔊 رفع سکوت":
        await update.effective_message.reply_text("💡 روی کاربر ریپلای کنید و دستور /unmute را بزنید.")
    elif text == "📊 لیست کاربران محدود شده":
        session = get_session()
        mutes = session.query(Mute).filter(Mute.group_id == update.effective_chat.id).all()
        if not mutes:
            await update.effective_message.reply_text("✅ در حال حاضر هیچ کاربر محدودی در این گروه وجود ندارد.")
        else:
            txt = "📊 لیست کاربران محدود شده:\n\n"
            for m in mutes:
                txt += f"👤 کاربر {m.user_id} تا زمان {m.until.strftime('%Y-%m-%d %H:%M')}\n"
            await update.effective_message.reply_text(txt, parse_mode=None)
        session.close()

    elif text == "🚫 مسدودسازی":
        await update.effective_message.reply_text("🚫 مدیریت لیست سیاه گروه:", reply_markup=get_bans_mgmt_menu())
    elif text == "🚫 بن کاربر":
        await update.effective_message.reply_text("💡 روی کاربر ریپلای کنید و دستور /ban را بزنید.")
    elif text == "♻️ رفع بن":
        await update.effective_message.reply_text("💡 دستور /unban را همراه با آیدی عددی کاربر بزنید.")

    elif text == "👤 اطلاعات کاربر":
        await update.effective_message.reply_text("👤 دریافت آمار و اطلاعات اعضا:", reply_markup=get_user_info_mgmt_menu())
    elif text == "🔎 پروفایل کاربر":
        await update.effective_message.reply_text("💡 روی کاربر ریپلای کنید و دستور /profile را بزنید.")
    elif text == "📈 آمار پیام‌ها":
        await update.effective_message.reply_text("💡 آمار دقیق پیام‌ها در بخش /profile قابل مشاهده است.")
    elif text == "⭐ XP و سطح":
        await update.effective_message.reply_text("💡 سطح و XP هر کاربر در پروفایل او نمایش داده می‌شود.")
    elif text == "💰 موجودی سکه":
        await update.effective_message.reply_text("💡 برای مشاهده موجودی سکه از دکمه موجودی کیف پول در منوی بانک استفاده کنید.")

    elif text == "🛡 امنیت":
        await update.effective_message.reply_text("🛡 تنظیمات امنیتی گروه:", reply_markup=get_security_mgmt_menu())
    elif text == "🔙 بازگشت به مدیریت اعضا":
        await update.effective_message.reply_text("👤 بازگشت به مدیریت اعضا:", reply_markup=get_member_mgmt_menu())

    raise ApplicationHandlerStop()

def get_handlers():
    nav_regex = "^(⚠️ اخطارها|➕ اخطار کاربر|📋 لیست اخطارها|🗑 حذف آخرین اخطار|🔄 پاک کردن همه اخطارها|🔇 محدودیت‌ها|🔇 سکوت کاربر|⏱ سکوت زمان‌دار|🔊 رفع سکوت|📊 لیست کاربران محدود شده|🚫 مسدودسازی|🚫 بن کاربر|♻️ رفع بن|👥 بن چند کاربر|📋 لیست بن‌ها|👤 اطلاعات کاربر|🔎 پروفایل کاربر|📈 آمار پیام‌ها|⭐ XP و سطح|💰 موجودی سکه|🛡 امنیت|🔙 بازگشت به مدیریت اعضا)$"
    return [
        CommandHandler("warn", warn_cmd),
        CommandHandler("warns", warns_cmd),
        CommandHandler("clearwarn", clearwarn_cmd),
        CommandHandler("mute", mute_cmd),
        CommandHandler("unmute", unmute_cmd),
        CommandHandler("ban", ban_cmd),
        CommandHandler("unban", unban_cmd),
        MessageHandler(filters.TEXT & filters.Regex(nav_regex), member_mgmt_buttons_handler),
        MessageHandler(filters.ALL, mute_checker),
    ]

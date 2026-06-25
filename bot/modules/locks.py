from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters, CommandHandler
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

async def lock_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat or update.effective_chat.type not in ["group", "supergroup"]:
        await update.message.reply_text("❌ این دستور فقط در گروه‌ها کاربرد دارد.")
        return

    if not await is_admin(update, context):
        await update.message.reply_text("❌ شما دسترسی لازم برای این کار را ندارید.")
        return

    if not context.args:
        await update.message.reply_text("💡 مثال:\n/lock links")
        return

    lock_type = context.args[0]
    session = get_session()
    group = session.query(Group).filter(Group.id == update.effective_chat.id).first()

    if not group:
        group = Group(id=update.effective_chat.id, title=update.effective_chat.title)
        session.add(group)

    # Map mapping user friendly names to db columns
    mapping = {
        "links": "lock_links",
        "usernames": "lock_usernames",
        "forward": "lock_forward",
        "photos": "lock_photos",
        "videos": "lock_videos",
        "files": "lock_files",
        "stickers": "lock_stickers",
        "gifs": "lock_gifs",
        "voice": "lock_voice",
        "contacts": "lock_contacts"
    }

    if lock_type not in mapping:
        await update.message.reply_text("❌ قفل نامعتبر است.\nلیست: links, usernames, forward, photos, videos, files, stickers, gifs, voice, contacts")
        session.close()
        return

    setattr(group, mapping[lock_type], True)
    session.commit()
    await update.message.reply_text(f"🔒 قفل {lock_type} در این گروه فعال شد.")
    session.close()

async def unlock_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat or update.effective_chat.type not in ["group", "supergroup"]:
        return

    if not await is_admin(update, context):
        await update.message.reply_text("❌ شما دسترسی لازم برای این کار را ندارید.")
        return

    if not context.args:
        await update.message.reply_text("💡 مثال:\n/unlock links")
        return

    lock_type = context.args[0]
    session = get_session()
    group = session.query(Group).filter(Group.id == update.effective_chat.id).first()

    if not group:
        session.close()
        return

    mapping = {
        "links": "lock_links",
        "usernames": "lock_usernames",
        "forward": "lock_forward",
        "photos": "lock_photos",
        "videos": "lock_videos",
        "files": "lock_files",
        "stickers": "lock_stickers",
        "gifs": "lock_gifs",
        "voice": "lock_voice",
        "contacts": "lock_contacts"
    }

    if lock_type not in mapping:
        await update.message.reply_text("❌ قفل نامعتبر است.")
        session.close()
        return

    setattr(group, mapping[lock_type], False)
    session.commit()
    await update.message.reply_text(f"🔓 قفل {lock_type} در این گروه غیرفعال شد.")
    session.close()

async def locks_status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat or update.effective_chat.type not in ["group", "supergroup"]:
        return

    session = get_session()
    group = session.query(Group).filter(Group.id == update.effective_chat.id).first()

    if not group:
        await update.message.reply_text("❌ تنظیماتی برای این گروه یافت نشد.")
        session.close()
        return

    def get_status(val): return "✅ فعال" if val else "❌ غیرفعال"

    text = (
        f"📊 وضعیت قفل‌های گروه {group.title}:\n\n"
        f"🔗 لینک: {get_status(group.lock_links)}\n"
        f"👤 یوزرنیم: {get_status(group.lock_usernames)}\n"
        f"↪️ فوروارد: {get_status(group.lock_forward)}\n"
        f"🖼 عکس: {get_status(group.lock_photos)}\n"
        f"🎬 ویدیو: {get_status(group.lock_videos)}\n"
        f"📁 فایل: {get_status(group.lock_files)}\n"
        f"🎭 استیکر: {get_status(group.lock_stickers)}\n"
        f"🎞 گیف: {get_status(group.lock_gifs)}\n"
        f"🎙 ویس: {get_status(group.lock_voice)}\n"
        f"📱 مخاطب: {get_status(group.lock_contacts)}\n"
    )
    await update.message.reply_text(text)
    session.close()

async def lock_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.effective_chat:
        return

    if update.effective_chat.type not in ["group", "supergroup"]:
        return

    # Skip admins
    if await is_admin(update, context):
        return

    session = get_session()
    group = session.query(Group).filter(Group.id == update.effective_chat.id).first()

    if not group:
        session.close()
        return

    msg = update.message
    deleted = False

    # Check Links
    if group.lock_links and msg.entities:
        for e in msg.entities:
            if e.type in ["url", "text_link"]:
                deleted = True
                break

    # Check Usernames
    if not deleted and group.lock_usernames and (msg.entities or msg.caption_entities):
        ents = (msg.entities or []) + (msg.caption_entities or [])
        for e in ents:
            if e.type == "mention":
                deleted = True
                break

    # Check Forward
    if not deleted and group.lock_forward and (msg.forward_from or msg.forward_from_chat):
        deleted = True

    # Check Media types
    if not deleted and group.lock_photos and msg.photo:
        deleted = True
    if not deleted and group.lock_videos and msg.video:
        deleted = True
    if not deleted and group.lock_files and msg.document:
        deleted = True
    if not deleted and group.lock_stickers and msg.sticker:
        deleted = True
    if not deleted and group.lock_gifs and msg.animation:
        deleted = True
    if not deleted and group.lock_voice and (msg.voice or msg.audio):
        deleted = True
    if not deleted and group.lock_contacts and msg.contact:
        deleted = True

    if deleted:
        try:
            await msg.delete()
        except:
            pass

    session.close()

def get_handlers():
    return [
        CommandHandler("lock", lock_cmd),
        CommandHandler("unlock", unlock_cmd),
        CommandHandler("locks", locks_status_cmd),
        MessageHandler(filters.ALL & ~filters.COMMAND, lock_filter),
    ]

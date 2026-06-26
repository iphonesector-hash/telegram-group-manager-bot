from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters, CommandHandler, ApplicationHandlerStop
from bot.database.session import get_session
from bot.database.models import Group
from bot.utils.helpers import is_admin
from bot.utils.keyboards import get_locks_menu

async def lock_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat or update.effective_chat.type not in ["group", "supergroup"]:
        await update.message.reply_text("❌ این دستور فقط در گروه‌ها کاربرد دارد.")
        return
    if not await is_admin(update, context):
        await update.message.reply_text("❌ شما دسترسی لازم برای این کار را ندارید.")
        return
    if not context.args:
        await update.message.reply_text("💡 مدیریت قفل‌ها:", reply_markup=get_locks_menu())
        return
    lock_type = context.args[0]
    session = get_session()
    group = session.query(Group).filter(Group.id == update.effective_chat.id).first()
    if not group:
        group = Group(id=update.effective_chat.id, title=update.effective_chat.title)
        session.add(group)
    mapping = {
        "links": "lock_links", "usernames": "lock_usernames", "forward": "lock_forward",
        "photos": "lock_photos", "videos": "lock_videos", "files": "lock_files",
        "stickers": "lock_stickers", "gifs": "lock_gifs", "voice": "lock_voice", "contacts": "lock_contacts"
    }
    if lock_type not in mapping:
        await update.message.reply_text("❌ قفل نامعتبر است.")
        session.close()
        return
    setattr(group, mapping[lock_type], True)
    session.commit()
    await update.message.reply_text(f"🔒 قفل {lock_type} فعال شد.")
    session.close()

async def lock_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context): return
    text = update.message.text
    mapping = {
        "🔗 لینک": "links", "👤 یوزرنیم": "usernames", "↪️ فوروارد": "forward",
        "🖼 عکس": "photos", "🎬 ویدیو": "videos", "📁 فایل": "files",
        "🎭 استیکر": "stickers", "🎞 گیف": "gifs", "🎙 ویس": "voice", "📱 مخاطب": "contacts"
    }
    if text in mapping:
        lock_type = mapping[text]
        session = get_session()
        group = session.query(Group).filter(Group.id == update.effective_chat.id).first()
        if not group:
            group = Group(id=update.effective_chat.id, title=update.effective_chat.title)
            session.add(group)
        attr = f"lock_{lock_type}"
        current = getattr(group, attr)
        setattr(group, attr, not current)
        session.commit()
        status = "فعال" if not current else "غیرفعال"
        icon = "🔒" if not current else "🔓"
        await update.message.reply_text(f"{icon} قفل {text.split()[-1]} {status} شد.")
        session.close()
        raise ApplicationHandlerStop()

async def lock_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.effective_chat: return
    if update.effective_chat.type not in ["group", "supergroup"]: return
    if await is_admin(update, context): return
    session = get_session()
    group = session.query(Group).filter(Group.id == update.effective_chat.id).first()
    if not group:
        session.close()
        return
    msg = update.message
    deleted = False
    if group.lock_links and msg.entities:
        for e in msg.entities:
            if e.type in ["url", "text_link"]: deleted = True; break
    if not deleted and group.lock_usernames and (msg.entities or msg.caption_entities):
        ents = (msg.entities or []) + (msg.caption_entities or [])
        for e in ents:
            if e.type == "mention": deleted = True; break
    if not deleted and group.lock_forward and (msg.forward_from or msg.forward_from_chat): deleted = True
    if not deleted and group.lock_photos and msg.photo: deleted = True
    if not deleted and group.lock_videos and msg.video: deleted = True
    if not deleted and group.lock_files and msg.document: deleted = True
    if not deleted and group.lock_stickers and msg.sticker: deleted = True
    if not deleted and group.lock_gifs and msg.animation: deleted = True
    if not deleted and group.lock_voice and (msg.voice or msg.audio): deleted = True
    if not deleted and group.lock_contacts and msg.contact: deleted = True
    if deleted:
        try: await msg.delete()
        except: pass
    session.close()

def get_handlers():
    return [
        CommandHandler("lock", lock_cmd),
        CommandHandler("locks", lock_cmd),
        MessageHandler(filters.TEXT & filters.Regex("^(🔗 لینک|👤 یوزرنیم|↪️ فوروارد|🖼 عکس|🎬 ویدیو|📁 فایل|🎭 استیکر|🎞 گیف|🎙 ویس|📱 مخاطب)$"), lock_button_handler),
        MessageHandler(filters.ALL & ~filters.COMMAND, lock_filter),
    ]

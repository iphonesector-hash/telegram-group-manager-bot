from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters, CommandHandler
from bot.database.session import get_session
from bot.database.models import Group

async def lock_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat or update.effective_chat.type not in ["group", "supergroup"]:
        await update.message.reply_text("این دستور فقط در گروه‌ها کاربرد دارد.")
        return

    if not context.args:
        await update.message.reply_text("مثال:\n/lock links")
        return

    lock_type = context.args[0]
    session = get_session()
    group = session.query(Group).filter(Group.id == update.effective_chat.id).first()

    if not group:
        group = Group(id=update.effective_chat.id, title=update.effective_chat.title)
        session.add(group)

    attr = f"lock_{lock_type}"
    if not hasattr(group, attr):
        await update.message.reply_text("❌ قفل نامعتبر است. لیست: links, photos, videos, stickers, forward")
        session.close()
        return

    setattr(group, attr, True)
    session.commit()
    await update.message.reply_text(f"🔒 قفل {lock_type} در این گروه فعال شد")
    session.close()

async def unlock_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat or update.effective_chat.type not in ["group", "supergroup"]:
        return

    if not context.args:
        await update.message.reply_text("مثال:\n/unlock links")
        return

    lock_type = context.args[0]
    session = get_session()
    group = session.query(Group).filter(Group.id == update.effective_chat.id).first()

    if not group:
        session.close()
        return

    attr = f"lock_{lock_type}"
    if not hasattr(group, attr):
        await update.message.reply_text("❌ قفل نامعتبر است.")
        session.close()
        return

    setattr(group, attr, False)
    session.commit()
    await update.message.reply_text(f"🔓 قفل {lock_type} در این گروه غیرفعال شد")
    session.close()

async def lock_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.effective_chat:
        return

    if update.effective_chat.type not in ["group", "supergroup"]:
        return

    session = get_session()
    group = session.query(Group).filter(Group.id == update.effective_chat.id).first()

    if not group:
        session.close()
        return

    msg = update.message
    deleted = False

    if group.lock_links and msg.entities:
        for e in msg.entities:
            if e.type in ["url", "text_link"]:
                deleted = True
                break

    if not deleted and group.lock_photos and msg.photo:
        deleted = True

    if not deleted and group.lock_videos and msg.video:
        deleted = True

    if not deleted and group.lock_stickers and msg.sticker:
        deleted = True

    if not deleted and group.lock_forward and (msg.forward_from or msg.forward_from_chat):
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
        MessageHandler(filters.ALL & ~filters.COMMAND, lock_filter),
    ]

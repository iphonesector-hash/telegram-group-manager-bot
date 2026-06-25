from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
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

async def panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat or update.effective_chat.type not in ["group", "supergroup"]:
        await update.message.reply_text("❌ این دستور فقط در گروه‌ها کاربرد دارد.")
        return

    if not await is_admin(update, context):
        await update.message.reply_text("❌ شما دسترسی لازم برای این کار را ندارید.")
        return

    keyboard = [
        [
            InlineKeyboardButton("🔒 قفل‌ها", callback_data="panel_locks"),
            InlineKeyboardButton("🌟 خوشامدگویی", callback_data="panel_welcome"),
        ],
        [
            InlineKeyboardButton("🛡 ضد اسپم", callback_data="panel_antispam"),
            InlineKeyboardButton("📜 قوانین", callback_data="panel_rules"),
        ],
        [
            InlineKeyboardButton("💰 سیستم مالی", callback_data="panel_economy"),
            InlineKeyboardButton("👤 مدیریت کاربران", callback_data="panel_users"),
        ],
        [
            InlineKeyboardButton("❌ بستن پنل", callback_data="panel_close"),
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    text = "🛠 **پنل مدیریت ربات SectorBot**\nلطفاً بخش مورد نظر را انتخاب کنید:"

    if update.message:
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    else:
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == "panel_close":
        await query.message.delete()
        return

    if data == "panel_main":
        await panel(update, context)
        return

    if data == "panel_locks":
        session = get_session()
        group = session.query(Group).filter(Group.id == update.effective_chat.id).first()

        def s(v): return "🔒" if v else "🔓"

        keyboard = [
            [
                InlineKeyboardButton(f"{s(group.lock_links)} لینک", callback_data="toggle_lock_links"),
                InlineKeyboardButton(f"{s(group.lock_usernames)} یوزرنیم", callback_data="toggle_lock_usernames"),
            ],
            [
                InlineKeyboardButton(f"{s(group.lock_forward)} فوروارد", callback_data="toggle_lock_forward"),
                InlineKeyboardButton(f"{s(group.lock_photos)} عکس", callback_data="toggle_lock_photos"),
            ],
            [
                InlineKeyboardButton(f"{s(group.lock_stickers)} استیکر", callback_data="toggle_lock_stickers"),
                InlineKeyboardButton(f"{s(group.lock_gifs)} گیف", callback_data="toggle_lock_gifs"),
            ],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="panel_main")]
        ]
        await query.edit_message_text("🔐 **تنظیمات قفل‌های گروه:**", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        session.close()

    elif data == "panel_welcome":
        session = get_session()
        group = session.query(Group).filter(Group.id == update.effective_chat.id).first()
        status = "✅ فعال" if group.welcome_enabled else "❌ غیرفعال"

        keyboard = [
            [InlineKeyboardButton(f"وضعیت: {status}", callback_data="toggle_welcome_enabled")],
            [InlineKeyboardButton("📝 تغییر متن خوشامد", callback_data="panel_setwelcome")],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="panel_main")]
        ]
        await query.edit_message_text("🌟 **تنظیمات خوشامدگویی:**", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        session.close()

    elif data == "panel_antispam":
        session = get_session()
        group = session.query(Group).filter(Group.id == update.effective_chat.id).first()
        status = "✅ فعال" if group.antispam_enabled else "❌ غیرفعال"

        keyboard = [
            [InlineKeyboardButton(f"وضعیت: {status}", callback_data="toggle_antispam_enabled")],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="panel_main")]
        ]
        await query.edit_message_text("🛡 **تنظیمات ضد اسپم:**", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        session.close()

    elif data == "panel_economy":
        session = get_session()
        group = session.query(Group).filter(Group.id == update.effective_chat.id).first()
        status = "✅ فعال" if group.economy_enabled else "❌ غیرفعال"

        keyboard = [
            [InlineKeyboardButton(f"وضعیت سیستم مالی: {status}", callback_data="toggle_economy_enabled")],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="panel_main")]
        ]
        await query.edit_message_text("💰 **تنظیمات سیستم مالی و سکه:**", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        session.close()

    elif data.startswith("toggle_"):
        attr = data.replace("toggle_", "")
        session = get_session()
        group = session.query(Group).filter(Group.id == update.effective_chat.id).first()

        if hasattr(group, attr):
            setattr(group, attr, not getattr(group, attr))
            session.commit()

        session.close()
        # Refresh the current sub-menu
        if "lock" in data:
            query.data = "panel_locks"
            await button_handler(update, context)
        elif "welcome" in data:
            query.data = "panel_welcome"
            await button_handler(update, context)
        elif "antispam" in data:
            query.data = "panel_antispam"
            await button_handler(update, context)
        elif "economy" in data:
            query.data = "panel_economy"
            await button_handler(update, context)

    elif data == "panel_rules":
        keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="panel_main")]]
        await query.edit_message_text("📜 برای تنظیم قوانین از دستور `/setrules متن قوانین` استفاده کنید.", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif data == "panel_users":
        keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="panel_main")]]
        await query.edit_message_text("👤 **مدیریت کاربران**\nبرای مدیریت کاربران از دستورات زیر استفاده کنید:\n\n/warn - اخطار به کاربر\n/mute - بی‌صدا کردن (دقیقه)\n/ban - اخراج و مسدود کردن\n/unmute - آزاد کردن کاربر", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif data == "panel_setwelcome":
        keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="panel_main")]]
        await query.edit_message_text("📝 **تنظیم متن خوشامد**\nبرای تغییر متن خوشامد از دستور زیر استفاده کنید:\n\n`/setwelcome متن جدید`", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

def get_panel_handlers():
    return [
        CommandHandler("panel", panel),
        CallbackQueryHandler(button_handler),
    ]

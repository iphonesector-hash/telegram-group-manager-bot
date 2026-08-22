from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ApplicationHandlerStop
from bot.utils.helpers import is_admin, get_group, get_user_badge
from bot.database.session import get_session
from bot.database.models import User


def _main():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎮 سرگرمی", callback_data="menu:ent"), InlineKeyboardButton("🛠 کاربردی", callback_data="menu:util")],
        [InlineKeyboardButton("👤 حساب کاربری", callback_data="menu:account"), InlineKeyboardButton("🏦 بانک و اقتصاد", callback_data="menu:economy")],
        [InlineKeyboardButton("🛡 مدیریت", callback_data="menu:admin"), InlineKeyboardButton("⚙️ تنظیمات", callback_data="menu:settings")],
        [InlineKeyboardButton("🤖 دستیار هوشمند", callback_data="menu:ai"), InlineKeyboardButton("🤝 پشتیبانی", url="https://t.me/sector_ad")],
    ])


def _back():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 منوی اصلی", callback_data="menu:main")]])


def _ent():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("😂 جوک", callback_data="act:joke"), InlineKeyboardButton("💡 دانستنی", callback_data="act:fact")],
        [InlineKeyboardButton("❓ معما", callback_data="act:riddle"), InlineKeyboardButton("📖 داستان", callback_data="act:story")],
        [InlineKeyboardButton("📜 فال حافظ", callback_data="act:hafez"), InlineKeyboardButton("🎲 تاس", callback_data="act:dice")],
        [InlineKeyboardButton("🪙 پرتاب سکه", callback_data="act:coin")],
        [InlineKeyboardButton("🔙 منوی اصلی", callback_data="menu:main")],
    ])


def _util():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🌐 مترجم", callback_data="util:translate"), InlineKeyboardButton("🧮 ماشین حساب", callback_data="util:calc")],
        [InlineKeyboardButton("⛅️ هواشناسی", callback_data="util:weather"), InlineKeyboardButton("📅 تاریخ و زمان", callback_data="util:time")],
        [InlineKeyboardButton("🔙 منوی اصلی", callback_data="menu:main")],
    ])


def _account():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("👤 پروفایل", callback_data="account:profile"), InlineKeyboardButton("🏆 رتبه", callback_data="account:rank")],
        [InlineKeyboardButton("📜 اخطارهای من", callback_data="account:warnings")],
        [InlineKeyboardButton("🔙 منوی اصلی", callback_data="menu:main")],
    ])


def _economy():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💰 موجودی", callback_data="eco:coins"), InlineKeyboardButton("🎁 هدیه روزانه", callback_data="eco:daily")],
        [InlineKeyboardButton("🏦 وام ۲۰۰", callback_data="eco:loan"), InlineKeyboardButton("📉 تسویه وام", callback_data="eco:repay")],
        [InlineKeyboardButton("🏆 ثروتمندترین‌ها", callback_data="eco:top")],
        [InlineKeyboardButton("🔙 منوی اصلی", callback_data="menu:main")],
    ])


def _admin():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 آمار گروه", callback_data="admin:stats"), InlineKeyboardButton("🛡 ضد اسپم", callback_data="admin:antispam")],
        [InlineKeyboardButton("🤖 هوش مصنوعی", callback_data="admin:ai"), InlineKeyboardButton("👋 خوشامدگویی", callback_data="admin:welcome")],
        [InlineKeyboardButton("📜 قوانین", callback_data="admin:rules"), InlineKeyboardButton("🆕 جلوگیری از ربات", callback_data="admin:prevent_bots")],
        [InlineKeyboardButton("🔙 منوی اصلی", callback_data="menu:main")],
    ])


def _user_row(update: Update):
    session = get_session()
    user = session.query(User).filter(User.id == update.effective_user.id).first() if update.effective_user else None
    return session, user


async def _account_text(update: Update, mode: str):
    session, user = _user_row(update)
    if not user:
        session.close()
        return "❌ هنوز پروفایلی برای شما ثبت نشده."
    if mode == "profile":
        rank = session.query(User).filter(User.coins > user.coins).count() + 1
        badge = get_user_badge(user)
        text = f"⚡ Sector Profile\n━━━━━━━━━━━━\n👤 {update.effective_user.full_name}\n🏅 {badge}\n🌟 سطح: {user.level}\n✨ XP: {user.xp}\n🪙 سکه: {user.coins:,}\n📨 پیام: {user.message_count:,}\n🏆 رتبه: {rank}"
    elif mode == "rank":
        total = session.query(User).count()
        wealth = session.query(User).filter(User.coins > user.coins).count() + 1
        activity = session.query(User).filter(User.message_count > user.message_count).count() + 1
        text = f"🏆 رتبه شما\n\n💰 ثروت: {wealth} از {total}\n📨 فعالیت: {activity} از {total}\n🌟 سطح: {user.level}"
    else:
        try:
            from bot.database.models import Warning
            n = session.query(Warning).filter(Warning.user_id == user.id).count()
            text = f"📜 سابقه اخطار\n\n⚠️ تعداد اخطارهای ثبت‌شده: {n}"
        except Exception:
            text = "📜 سابقه اخطار در دسترس نیست."
    session.close()
    return text


async def _economy_text(update: Update, action: str):
    import datetime
    session, user = _user_row(update)
    if not user:
        session.close()
        return "❌ حساب شما هنوز ساخته نشده."
    if action == "coins":
        text = f"💳 SectorBank\n\n👛 کیف پول: {user.coins:,}\n🏦 بانک: {user.bank_balance:,}\n💎 دارایی: {user.coins + user.bank_balance:,}\n📛 بدهی: {user.loan_balance:,}"
    elif action == "daily":
        now = datetime.datetime.now(datetime.timezone.utc)
        last = user.last_daily_claim
        if last and last.tzinfo is None:
            last = last.replace(tzinfo=datetime.timezone.utc)
        if last and now - last < datetime.timedelta(hours=24):
            left = datetime.timedelta(hours=24) - (now - last)
            h = int(left.total_seconds()) // 3600
            m = (int(left.total_seconds()) % 3600) // 60
            text = f"⏳ هدیه امروز را گرفتی؛ {h} ساعت و {m} دقیقه دیگه دوباره بیا."
        else:
            user.coins += 50
            user.last_daily_claim = now
            session.commit()
            text = f"🎁 +50 سکه گرفتی\n👛 موجودی: {user.coins:,}"
    elif action == "loan":
        if user.loan_balance > 0:
            text = f"📛 اول وام قبلی را تسویه کن. بدهی: {user.loan_balance:,}"
        else:
            user.coins += 200
            user.loan_balance = 220
            session.commit()
            text = "🏦 ۲۰۰ سکه وام گرفتی.\n📛 بازپرداخت: ۲۲۰ سکه"
    elif action == "repay":
        if user.loan_balance <= 0:
            text = "✅ وام فعالی نداری."
        elif user.coins < user.loan_balance:
            text = f"❌ برای تسویه {user.loan_balance:,} سکه لازم داری. موجودی: {user.coins:,}"
        else:
            debt = user.loan_balance
            user.coins -= debt
            user.loan_balance = 0
            session.commit()
            text = "✅ وام کامل تسویه شد."
    else:
        users = session.query(User).order_by(User.coins.desc()).limit(10).all()
        text = "🏆 ثروتمندترین‌های سکتور\n\n" + "\n".join(f"{i+1}. {u.first_name} — 🪙 {u.coins:,}" for i, u in enumerate(users))
    session.close()
    return text


async def _toggle(update: Update, attr: str, label: str):
    session = get_session()
    group = get_group(session, update.effective_chat.id)
    if not group or not hasattr(group, attr):
        session.close()
        return "❌ این تنظیم برای این گروه در دسترس نیست."
    setattr(group, attr, not bool(getattr(group, attr)))
    session.commit()
    state = "فعال ✅" if getattr(group, attr) else "غیرفعال ⛔️"
    session.close()
    return f"{label}: {state}"


async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    if not q:
        return
    await q.answer()
    data = q.data or ""

    if data == "menu:main": return await q.edit_message_text("🏠 منوی اصلی SectorBot", reply_markup=_main())
    if data == "menu:ent": return await q.edit_message_text("🎮 سرگرمی و بازی", reply_markup=_ent())
    if data == "menu:util": return await q.edit_message_text("🛠 ابزارهای کاربردی", reply_markup=_util())
    if data == "menu:account": return await q.edit_message_text("👤 حساب کاربری", reply_markup=_account())
    if data == "menu:economy": return await q.edit_message_text("🏦 بانک و اقتصاد", reply_markup=_economy())
    if data == "menu:ai":
        msg = "🤖 همین‌جا هر سوالی داری بپرس." if update.effective_chat.type == "private" else "🤖 در گروه من را با «سکتور» صدا بزن، منشن کن یا روی پیامم ریپلای کن."
        return await q.edit_message_text(msg, reply_markup=_back())
    if data in ("menu:admin", "menu:settings"):
        if update.effective_chat.type == "private": return await q.edit_message_text("⚙️ تنظیمات مدیریتی فقط داخل گروه قابل استفاده است.", reply_markup=_back())
        if not await is_admin(update, context): return await q.answer("این بخش مخصوص مدیران گروه است.", show_alert=True)
        return await q.edit_message_text("🛡 مدیریت گروه", reply_markup=_admin())

    if data.startswith("account:"):
        return await q.edit_message_text(await _account_text(update, data.split(":",1)[1]), reply_markup=_account())
    if data.startswith("eco:"):
        return await q.edit_message_text(await _economy_text(update, data.split(":",1)[1]), reply_markup=_economy())
    if data.startswith("admin:"):
        if update.effective_chat.type == "private" or not await is_admin(update, context): return await q.answer("فقط مدیران گروه", show_alert=True)
        action = data.split(":",1)[1]
        if action == "stats":
            n = await context.bot.get_chat_member_count(update.effective_chat.id)
            text = f"📊 آمار گروه\n\n👥 اعضا: {n}\n🤖 ربات: آنلاین 🟢"
        elif action == "antispam": text = await _toggle(update,"antispam_enabled","🛡 ضد اسپم")
        elif action == "ai": text = await _toggle(update,"ai_enabled","🤖 هوش مصنوعی")
        elif action == "welcome": text = await _toggle(update,"welcome_enabled","👋 خوشامدگویی")
        elif action == "rules": text = await _toggle(update,"rules_enabled","📜 قوانین")
        else: text = await _toggle(update,"prevent_bots","🆕 جلوگیری از ورود ربات")
        return await q.edit_message_text(text, reply_markup=_admin())

    if data.startswith("act:"):
        from bot.modules.ai import get_new_joke, get_new_fact, hafez_fortune
        from bot.modules.entertainment import get_riddle_cmd, get_story_cmd, dice_cmd, coin_cmd
        a = data.split(":",1)[1]
        try:
            if a == "joke": await get_new_joke(update,context)
            elif a == "fact": await get_new_fact(update,context)
            elif a == "riddle": await get_riddle_cmd(update,context)
            elif a == "story": await get_story_cmd(update,context)
            elif a == "hafez": await hafez_fortune(update,context)
            elif a == "dice": await dice_cmd(update,context)
            elif a == "coin": await coin_cmd(update,context)
        except ApplicationHandlerStop:
            pass
        return

    if data == "util:translate": return await q.edit_message_text("🌐 متن را این‌طور بفرست:\nترجمه: متن موردنظر", reply_markup=_util())
    if data == "util:calc": return await q.edit_message_text("🧮 عبارت را بفرست؛ مثال: 10 + 5", reply_markup=_util())
    if data == "util:weather": return await q.edit_message_text("⛅️ بنویس: هوای تهران", reply_markup=_util())
    if data == "util:time":
        import datetime
        now=datetime.datetime.now()
        return await q.edit_message_text(f"📅 {now:%Y-%m-%d}\n🕒 {now:%H:%M:%S}", reply_markup=_util())


async def legacy_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_message or not update.effective_message.text:
        return
    text = update.effective_message.text
    mapping = {
        "🎮 سرگرمی": ("🎮 سرگرمی و بازی", _ent()),
        "🛠 کاربردی": ("🛠 ابزارهای کاربردی", _util()),
        "👤 حساب کاربری": ("👤 حساب کاربری", _account()),
        "🏦 بانک و اقتصاد": ("🏦 بانک و اقتصاد", _economy()),
        "🔙 بازگشت به منوی اصلی": ("🏠 منوی اصلی SectorBot", _main()),
    }
    if text in mapping:
        title,kb = mapping[text]
        if update.effective_chat.type != "private":
            try: await update.effective_message.delete()
            except Exception: pass
        await context.bot.send_message(update.effective_chat.id,title,reply_markup=kb)
        raise ApplicationHandlerStop()
    if text in ("🛡 مدیریت","⚙️ تنظیمات"):
        if update.effective_chat.type == "private":
            await context.bot.send_message(update.effective_chat.id,"⚙️ تنظیمات مدیریتی فقط داخل گروه قابل استفاده است.",reply_markup=_back())
        elif await is_admin(update,context):
            try: await update.effective_message.delete()
            except Exception: pass
            await context.bot.send_message(update.effective_chat.id,"🛡 مدیریت گروه",reply_markup=_admin())
        else:
            await context.bot.send_message(update.effective_chat.id,"❌ این بخش مخصوص مدیران گروه است.")
        raise ApplicationHandlerStop()
    if text == "🤖 دستیار هوشمند":
        msg = "🤖 همین‌جا هر سوالی داری بپرس." if update.effective_chat.type == "private" else "🤖 من را با «سکتور» صدا بزن، منشن کن یا روی پیامم ریپلای کن."
        await context.bot.send_message(update.effective_chat.id,msg,reply_markup=_back())
        raise ApplicationHandlerStop()


async def panel_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_text("🏠 منوی اصلی SectorBot", reply_markup=_main())
    raise ApplicationHandlerStop()


def get_panel_handlers():
    nav = "^(🛡 مدیریت|👤 حساب کاربری|🏦 بانک و اقتصاد|🎮 سرگرمی|🛠 کاربردی|⚙️ تنظیمات|🤖 دستیار هوشمند|🔙 بازگشت به منوی اصلی)$"
    return [
        CommandHandler("panel", panel_cmd),
        CallbackQueryHandler(menu_callback, pattern=r"^(menu|act|util|account|eco|admin):"),
        MessageHandler(filters.TEXT & filters.Regex(nav), legacy_button),
    ]

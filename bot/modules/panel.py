import datetime
import os

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, WebAppInfo
from telegram.error import BadRequest
from telegram.ext import ApplicationHandlerStop, CallbackQueryHandler, CommandHandler, ContextTypes, MessageHandler, filters

from bot.database.models import AppSetting, User
from bot.database.session import get_session
from bot.modules.ai import get_ai_response
from bot.modules.sector_social import show_sector_reply_actions
from bot.utils.helpers import get_group, get_user_badge, is_admin
from bot.utils.keyboards import get_main_menu

MINI_APP_URL = os.getenv("MINI_APP_URL", "https://isectorland-miniapp.vercel.app").split("?", 1)[0]
MAIN_APP_LINK = "https://t.me/iSectorlandbot?startapp=sector"


def B(text, data=None, style="primary", url=None, web_app=None):
    return InlineKeyboardButton(text, callback_data=data, url=url, web_app=web_app, style=style)


def _topic_id(update):
    return int(getattr(update.effective_message, "message_thread_id", 0) or 0)


def _panel_key(update):
    return f"group_panel:{update.effective_chat.id}:{_topic_id(update)}"


def _load_panel_id(update):
    session = get_session()
    try:
        row = session.query(AppSetting).filter(AppSetting.key == _panel_key(update)).first()
        value = row.value if row and isinstance(row.value, dict) else {}
        return int(value.get("message_id")) if value.get("message_id") else None
    finally:
        session.close()


def _save_panel_id(update, message_id):
    session = get_session()
    try:
        key = _panel_key(update)
        row = session.query(AppSetting).filter(AppSetting.key == key).first()
        value = {"message_id": int(message_id), "thread_id": _topic_id(update)}
        if row:
            row.value = value
            row.updated_at = datetime.datetime.utcnow()
        else:
            session.add(AppSetting(key=key, value=value))
        session.commit()
    finally:
        session.close()


async def _delete_press(update):
    if update.effective_chat.type == "private" or not update.effective_message:
        return
    try:
        await update.effective_message.delete()
    except Exception:
        pass


def _back(rows=None):
    rows = list(rows or [])
    rows.append([B("بازگشت", "gp:nav:main", "primary")])
    return InlineKeyboardMarkup(rows)


def _main_inline():
    return InlineKeyboardMarkup([
        [B("حساب کاربری", "gp:nav:profile", "primary"), B("اقتصاد", "gp:nav:economy", "success")],
        [B("سرگرمی", "gp:nav:fun", "primary"), B("کاربردی", "gp:nav:tools", "primary")],
        [B("سکتور کوچولو", "gp:nav:sector", "success"), B("مدیریت", "gp:nav:admin", "danger")],
        [B("Mini App", url=MAIN_APP_LINK, style="primary")],
    ])


def _nav(name):
    if name == "profile":
        return "حساب کاربری\nهمه‌چیز روی همین پنل نمایش داده می‌شود.", _back([[B("پروفایل", "gp:act:profile"), B("رتبه", "gp:act:rank")]])
    if name == "economy":
        return "SectorBank\nعملیات اقتصادی را انتخاب کن.", _back([[B("موجودی", "gp:act:coins"), B("هدیه روزانه", "gp:act:daily", "success")], [B("برترین‌های ثروت", "gp:act:wealth", "success")]])
    if name == "fun":
        return "سرگرمی\nنتیجه هم روی همین پنل نمایش داده می‌شود و پیام تازه نمی‌سازد.", _back([[B("معما", "gp:act:riddle"), B("دانستنی", "gp:act:fact")], [B("داستان", "gp:act:story"), B("فال حافظ", "gp:act:hafez")], [B("جرأت", "gp:act:dare", "danger"), B("حقیقت", "gp:act:truth", "success")]])
    if name == "tools":
        return "ابزارهای کاربردی\nراهنماها به‌صورت Popup نمایش داده می‌شوند.", _back([[B("مترجم", "gp:hint:translate"), B("ماشین حساب", "gp:hint:calc")], [B("هواشناسی", "gp:hint:weather"), B("تاریخ و زمان", "gp:act:time", "success")]])
    if name == "sector":
        return "Sector Companion\nرشد و فروشگاه در Mini App؛ تعامل اجتماعی با Reply روی پیام کاربران.", _back([[B("باز کردن Sector", url=MAIN_APP_LINK, style="success")]])
    if name == "settings":
        return "تنظیمات\nبدون ترک Topic در دسترس است.", _back([[B("تنظیمات AI", "gp:hint:ai_settings"), B("Mini App", url=MAIN_APP_LINK, style="success")]])
    if name == "assistant":
        return "دستیار هوشمند\nسکتور را صدا بزن، منشن کن یا روی پیامش Reply کن.", _back()
    if name == "support":
        return "پشتیبانی SectorLand", _back([[B("ارتباط با پشتیبانی", url="https://t.me/sector_ad", style="success")]])
    if name == "locks":
        return "قفل‌های گروه\nهر دکمه همان قفل را درجا روشن/خاموش می‌کند.", _back([
            [B("لینک", "gp:lock:links", "danger"), B("یوزرنیم", "gp:lock:usernames", "danger")],
            [B("فوروارد", "gp:lock:forward", "danger"), B("عکس", "gp:lock:photos", "danger")],
            [B("ویدیو", "gp:lock:videos", "danger"), B("فایل", "gp:lock:files", "danger")],
            [B("استیکر", "gp:lock:stickers", "danger"), B("گیف", "gp:lock:gifs", "danger")],
            [B("ویس", "gp:lock:voice", "danger"), B("مخاطب", "gp:lock:contacts", "danger")],
        ])
    if name == "admin":
        return "مدیریت گروه\nمنوی پایین ثابت می‌ماند و ابزارها در همین پنل باز می‌شوند.", _back([[B("قفل‌ها", "gp:nav:locks", "danger"), B("مدیریت اعضا", "gp:hint:members", "danger")], [B("خوشامدگویی", "gp:hint:welcome"), B("قوانین", "gp:hint:rules")], [B("اخطار", "gp:hint:warn", "danger"), B("آمار گروه", "gp:act:groupstats", "success")]])
    return "SectorLand Control Panel\nیکی از بخش‌ها را انتخاب کن.", _main_inline()


async def _render_group_panel(update, context, text, markup):
    message_id = _load_panel_id(update)
    if message_id:
        try:
            await context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=message_id, text=text, reply_markup=markup)
            return
        except BadRequest as exc:
            if "message is not modified" in str(exc).lower():
                return
        except Exception:
            pass
    sent = await context.bot.send_message(chat_id=update.effective_chat.id, text=text, reply_markup=markup, message_thread_id=_topic_id(update) or None)
    _save_panel_id(update, sent.message_id)


async def panel_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == "private":
        await update.effective_message.reply_text("SectorLand Control Panel", reply_markup=get_main_menu())
    else:
        await _render_group_panel(update, context, "SectorLand Control Panel\nاین پنل بی‌صدا با Edit به‌روزرسانی می‌شود.", _main_inline())
    raise ApplicationHandlerStop()


def _user_stats(user, rank):
    return f"پروفایل Sector\n\n{user.first_name}\nنشان: {get_user_badge(user)}\nسطح: {user.level}\nXP: {user.xp:,}\nسکه: {user.coins:,}\nپیام‌ها: {user.message_count:,}\nرتبه: {rank}"


async def _ai_panel_result(query, prompt, user_query):
    try:
        result = await get_ai_response(prompt, user_query)
    except Exception:
        result = None
    await query.edit_message_text((result or "فعلاً هسته هوشمند پاسخ نداد؛ دوباره تلاش کن.")[:3500], reply_markup=_back())


async def group_panel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data or ""
    if not data.startswith("gp:"):
        return
    _, kind, value = (data.split(":", 2) + ["", ""])[:3]

    if kind == "nav":
        if value in ("admin", "locks") and not await is_admin(update, context):
            await query.answer("این بخش مخصوص مدیران است.", show_alert=True)
            raise ApplicationHandlerStop()
        await query.answer()
        text, markup = _nav(value)
        await query.edit_message_text(text, reply_markup=markup)
        raise ApplicationHandlerStop()

    if kind == "hint":
        hints = {"translate":"برای ترجمه بنویس: ترجمه: متن","calc":"عبارت را مستقیم بفرست؛ مثل 25 * 4 + 10","weather":"بنویس: هوای تهران","warn":"روی پیام کاربر Reply کن و /warn دلیل را بزن.","members":"برای عملیات عضو روی پیام او Reply کن و /mute، /kick یا /ban بزن.","welcome":"تنظیمات خوشامدگویی از مدیریت گروه انجام می‌شود.","rules":"قوانین گروه از بخش مدیریت قابل تنظیم است.","ai_settings":"تنظیمات پیشرفته AI از Mini App انجام می‌شود."}
        await query.answer(hints.get(value, "راهنما موجود نیست."), show_alert=True)
        raise ApplicationHandlerStop()

    if kind == "lock":
        if not await is_admin(update, context):
            await query.answer("این بخش مخصوص مدیران است.", show_alert=True)
            raise ApplicationHandlerStop()
        mapping = {"links":"lock_links","usernames":"lock_usernames","forward":"lock_forward","photos":"lock_photos","videos":"lock_videos","files":"lock_files","stickers":"lock_stickers","gifs":"lock_gifs","voice":"lock_voice","contacts":"lock_contacts"}
        attr = mapping.get(value)
        if not attr:
            await query.answer("قفل نامعتبر است.", show_alert=True)
            raise ApplicationHandlerStop()
        session = get_session()
        try:
            group = get_group(session, update.effective_chat.id, update.effective_chat.title or "")
            enabled = not bool(getattr(group, attr))
            setattr(group, attr, enabled)
            session.commit()
        finally:
            session.close()
        await query.answer("فعال شد" if enabled else "غیرفعال شد")
        text, markup = _nav("locks")
        await query.edit_message_text(text, reply_markup=markup)
        raise ApplicationHandlerStop()

    await query.answer()
    session = get_session()
    try:
        user = session.query(User).filter(User.id == query.from_user.id).first()
        if value in {"profile","rank","coins","daily","wealth"} and not user:
            await query.edit_message_text("حساب کاربر پیدا نشد.", reply_markup=_back())
            raise ApplicationHandlerStop()
        if value == "profile":
            rank = session.query(User).filter(User.coins > user.coins).count() + 1
            await query.edit_message_text(_user_stats(user, rank), reply_markup=_back())
        elif value == "rank":
            total = session.query(User).count(); wealth = session.query(User).filter(User.coins > user.coins).count()+1; activity = session.query(User).filter(User.message_count > user.message_count).count()+1
            await query.edit_message_text(f"رتبه شما\n\nثروت: {wealth} از {total}\nفعالیت: {activity} از {total}\nسطح: {user.level}", reply_markup=_back())
        elif value == "coins":
            await query.edit_message_text(f"SectorBank\n\nکیف پول: {user.coins:,}\nبانک: {user.bank_balance:,}\nدارایی: {user.coins+user.bank_balance:,}\nبدهی: {user.loan_balance:,}", reply_markup=_back())
        elif value == "daily":
            now = datetime.datetime.now(datetime.timezone.utc); last = user.last_daily_claim
            if last and last.tzinfo is None: last = last.replace(tzinfo=datetime.timezone.utc)
            if last and now-last < datetime.timedelta(hours=24):
                left=datetime.timedelta(hours=24)-(now-last); text=f"هدیه امروز قبلاً دریافت شده.\n{int(left.total_seconds()//3600)} ساعت و {int((left.total_seconds()%3600)//60)} دقیقه دیگر دوباره تلاش کن."
            else:
                vip=user.vip_until
                if vip and vip.tzinfo is None: vip=vip.replace(tzinfo=datetime.timezone.utc)
                reward=75 if vip and vip>now else 50; user.coins+=reward; user.last_daily_claim=now; session.commit(); text=f"هدیه روزانه دریافت شد.\n+{reward} سکه\nموجودی: {user.coins:,}"
            await query.edit_message_text(text, reply_markup=_back())
        elif value == "wealth":
            rows=session.query(User).order_by(User.coins.desc()).limit(10).all(); lines=[f"{i+1}. {u.first_name} — {u.coins:,}" for i,u in enumerate(rows)]
            await query.edit_message_text("برترین‌های ثروت\n\n"+("\n".join(lines) if lines else "هنوز داده‌ای نیست."), reply_markup=_back())
        elif value == "time":
            now=datetime.datetime.now(); await query.edit_message_text(f"تاریخ و زمان\n{now.strftime('%Y-%m-%d')} • {now.strftime('%H:%M:%S')}", reply_markup=_back())
        elif value == "groupstats":
            count=await context.bot.get_chat_member_count(update.effective_chat.id); await query.edit_message_text(f"آمار گروه\nاعضا: {count:,}\nوضعیت ربات: آنلاین", reply_markup=_back())
        elif value in {"riddle","fact","story","hafez","dare","truth"}:
            prompts={"riddle":"یک معمای فارسی کوتاه و تازه بگو و پاسخ را آخرش بنویس.","fact":"یک دانستنی علمی معتبر و کوتاه فارسی بگو.","story":"یک داستان خیلی کوتاه علمی‌تخیلی فارسی بنویس.","hafez":"یک فال حافظ فارسی بده؛ جنبه سرگرمی را بگو و شعر جعل نکن.","dare":"یک جرأت امن و بامزه برای گروه تلگرام پیشنهاد بده.","truth":"یک سؤال حقیقت جالب و غیرتوهین‌آمیز بپرس."}
            session.close(); session=None; await _ai_panel_result(query, "فارسی، کوتاه و مناسب فضای عمومی پاسخ بده. "+prompts[value], value)
    finally:
        if session is not None: session.close()
    raise ApplicationHandlerStop()


async def menu_navigation_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_message or not update.effective_message.text:
        return
    text = update.effective_message.text.strip()
    if update.effective_chat.type == "private":
        from bot.utils.keyboards import get_economy_menu, get_entertainment_menu, get_settings_menu, get_user_menu, get_utility_menu
        mapping={"🎮 سرگرمی":("سرگرمی",get_entertainment_menu()),"🛠 کاربردی":("ابزارهای کاربردی",get_utility_menu()),"👤 حساب کاربری":("حساب کاربری",get_user_menu()),"🏦 بانک و اقتصاد":("بانک و اقتصاد",get_economy_menu()),"⚙️ تنظیمات":("تنظیمات",get_settings_menu())}
        if text in mapping:
            title,markup=mapping[text]; await update.effective_message.reply_text(title,reply_markup=markup); raise ApplicationHandlerStop()
        if text in ("سکتور کوچولو","🤖 سکتور کوچولو"):
            await update.effective_message.reply_text("Sector Companion",reply_markup=InlineKeyboardMarkup([[B("باز کردن Sector",style="success",web_app=WebAppInfo(url=MINI_APP_URL))]])); raise ApplicationHandlerStop()
        return
    replied=update.effective_message.reply_to_message
    if text in ("سکتور کوچولو","🤖 سکتور کوچولو") and replied and replied.from_user and not replied.from_user.is_bot:
        opened=await show_sector_reply_actions(update,context,replied.from_user); await _delete_press(update)
        if opened: raise ApplicationHandlerStop()
    nav_map={"👤 حساب کاربری":"profile","🏦 بانک و اقتصاد":"economy","🎮 سرگرمی":"fun","🛠 کاربردی":"tools","سکتور کوچولو":"sector","🤖 سکتور کوچولو":"sector","🛡 مدیریت":"admin","⚙️ تنظیمات":"settings","🤖 دستیار هوشمند":"assistant","🤝 پشتیبانی":"support","🔙 بازگشت به منوی اصلی":"main"}
    if text not in nav_map:return
    if nav_map[text]=="admin" and not await is_admin(update,context): await _delete_press(update); raise ApplicationHandlerStop()
    await _delete_press(update); panel_text,markup=_nav(nav_map[text]); await _render_group_panel(update,context,panel_text,markup); raise ApplicationHandlerStop()


def get_panel_handlers():
    nav_regex="^(🛡 مدیریت|👤 حساب کاربری|🏦 بانک و اقتصاد|🎮 سرگرمی|🛠 کاربردی|⚙️ تنظیمات|🤖 دستیار هوشمند|🤖 سکتور کوچولو|سکتور کوچولو|🤝 پشتیبانی|🔙 بازگشت به منوی اصلی)$"
    return [CommandHandler("panel",panel_cmd),CallbackQueryHandler(group_panel_callback,pattern=r"^gp:"),MessageHandler(filters.TEXT & filters.Regex(nav_regex),menu_navigation_handler)]

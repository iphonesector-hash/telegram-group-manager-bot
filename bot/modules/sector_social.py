import html
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationHandlerStop, CallbackQueryHandler, CommandHandler, ContextTypes
from bot.database.models import User
from bot.database.session import get_session
from bot.services import sector_pet as service
from bot.services.sector_economy import appearance_icons

MAIN_APP_LINK='https://t.me/iSectorlandbot?startapp=sector'

def _reply_target(update):
    m=update.effective_message;r=m.reply_to_message if m else None;u=r.from_user if r and r.from_user else None
    return None if not u or u.is_bot or u.id==update.effective_user.id else u

def _gear_line(pet):
    items=appearance_icons(pet)
    return 'بدون تجهیزات' if not items else ' '.join(i['icon'] for i in items)+'  '+' • '.join(i['title'] for i in items[:4])

def _keyboard(actor,target):
    p=f'sectorx:{actor}:{target}:'
    return InlineKeyboardMarkup([[InlineKeyboardButton('⚔️ دوئل',callback_data=p+'battle',style='danger'),InlineKeyboardButton('🎁 هدیه ۵۰',callback_data=p+'gift',style='success')],[InlineKeyboardButton('🏠 ملاقات',callback_data=p+'visit',style='success'),InlineKeyboardButton('🐾 کارت سکتور',callback_data=p+'profile',style='primary')],[InlineKeyboardButton('sector',url=MAIN_APP_LINK,style='primary')]])

def _card(a,ap,t,tp):
    return ('🐾 <b>تعامل سکتورها</b>\n\n'+f'🤖 <b>{html.escape(ap.name)}</b> • {html.escape(a.first_name or "کاربر")} • Lv.{service.level_from_xp(ap.xp)}\n👕 {_gear_line(ap)}\n\nVS / WITH\n\n'+f'🤖 <b>{html.escape(tp.name)}</b> • {html.escape(t.first_name or "کاربر")} • Lv.{service.level_from_xp(tp.xp)}\n👕 {_gear_line(tp)}\n\nیک اکشن انتخاب کن؛ همین کارت به‌روزرسانی می‌شود تا تاپیک شلوغ نشود.')

async def show_sector_reply_actions(update:Update,context:ContextTypes.DEFAULT_TYPE,target=None):
    if not update.effective_chat or update.effective_chat.type=='private':return False
    target=target or _reply_target(update)
    if not target:return False
    s=get_session()
    try:
        a=s.query(User).filter(User.id==update.effective_user.id).first();t=s.query(User).filter(User.id==target.id).first()
        if not a or not t:await update.effective_message.reply_text('🐾 هر دو کاربر باید یک‌بار ربات را /start کرده باشند.');return True
        ap=service.get_or_create_pet(s,a.id);tp=service.get_or_create_pet(s,t.id);s.commit();await update.effective_message.reply_text(_card(a,ap,t,tp),parse_mode='HTML',reply_markup=_keyboard(a.id,t.id));return True
    finally:s.close()

async def sector_actions_command(update,context):
    if update.effective_chat.type=='private':await update.effective_message.reply_text('🐾 این دستور داخل گروه و روی Reply یک کاربر استفاده می‌شود.');raise ApplicationHandlerStop()
    if not await show_sector_reply_actions(update,context):await update.effective_message.reply_text('🐾 روی پیام یک کاربر Reply کن و /sectoractions بزن.')
    raise ApplicationHandlerStop()

async def sector_social_callback(update,context):
    q=update.callback_query
    try:_,ar,tr,action=q.data.split(':',3);aid,tid=int(ar),int(tr)
    except Exception:await q.answer('اکشن نامعتبر است.',show_alert=True);return
    if q.from_user.id!=aid:await q.answer('این پنل برای صاحب سکتوریه که اکشن رو شروع کرده.',show_alert=True);return
    s=get_session()
    try:
        a=s.query(User).filter(User.id==aid).first();t=s.query(User).filter(User.id==tid).first()
        if not a or not t:await q.answer('یکی از حساب‌ها پیدا نشد.',show_alert=True);return
        ap=service.get_or_create_pet(s,aid);tp=service.get_or_create_pet(s,tid)
        if action=='profile':
            s.commit();text=f'🐾 <b>کارت {html.escape(tp.name)}</b>\n\n👤 صاحب: {html.escape(t.first_name or "کاربر")}\n⭐ سطح: {service.level_from_xp(tp.xp)}\n🔥 Streak: {int(tp.streak_days or 0)} روز\n🧠 دانش: {int(tp.knowledge or 0)}٪\n❤️ سلامت: {int(tp.health or 0)}٪\n👕 تجهیزات: {_gear_line(tp)}';await q.answer();await q.edit_message_text(text,parse_mode='HTML',reply_markup=_keyboard(aid,tid));return
        result=service.social_action(s,aid,tid,action)
        if result.get('status')!='success':s.rollback();await q.answer(result.get('message') or 'اکشن انجام نشد.',show_alert=True);return
        s.commit();ap=service.get_or_create_pet(s,aid);tp=service.get_or_create_pet(s,tid);text=f'{_card(a,ap,t,tp)}\n\n━━━━━━━━━━\n<b>{html.escape(result["message"])}</b>';await q.answer('انجام شد 🐾');await q.edit_message_text(text,parse_mode='HTML',reply_markup=_keyboard(aid,tid))
    finally:s.close()

def get_handlers():return [CommandHandler('sectoractions',sector_actions_command),CallbackQueryHandler(sector_social_callback,pattern=r'^sectorx:\d+:\d+:(battle|gift|visit|profile)$')]

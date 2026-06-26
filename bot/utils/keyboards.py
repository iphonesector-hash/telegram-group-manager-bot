from telegram import ReplyKeyboardMarkup, KeyboardButton

def get_main_menu():
    keyboard = [
        [KeyboardButton("🛡 مدیریت"), KeyboardButton("👤 حساب کاربری")],
        [KeyboardButton("🏦 بانک و اقتصاد"), KeyboardButton("🎮 سرگرمی")],
        [KeyboardButton("🛠 کاربردی"), KeyboardButton("🤖 دستیار هوشمند")],
        [KeyboardButton("⚙️ تنظیمات"), KeyboardButton("🆘 پشتیبانی")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_admin_menu():
    keyboard = [
        [KeyboardButton("🔒 قفل‌های گروه"), KeyboardButton("🌟 خوشامدگویی")],
        [KeyboardButton("🛡 ضد اسپم"), KeyboardButton("📜 قوانین")],
        [KeyboardButton("👤 مدیریت اعضا"), KeyboardButton("💰 تنظیمات اقتصاد")],
        [KeyboardButton("🔙 بازگشت به منوی اصلی")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_locks_menu():
    keyboard = [
        [KeyboardButton("🔗 لینک"), KeyboardButton("👤 یوزرنیم")],
        [KeyboardButton("↪️ فوروارد"), KeyboardButton("🖼 عکس")],
        [KeyboardButton("🎬 ویدیو"), KeyboardButton("📁 فایل")],
        [KeyboardButton("🎭 استیکر"), KeyboardButton("🎞 گیف")],
        [KeyboardButton("🎙 ویس"), KeyboardButton("📱 مخاطب")],
        [KeyboardButton("🔙 بازگشت به مدیریت")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_user_menu():
    keyboard = [
        [KeyboardButton("📊 پروفایل من")],
        [KeyboardButton("🏆 رتبه جهانی"), KeyboardButton("📜 سوابق اخطار")],
        [KeyboardButton("🔙 بازگشت به منوی اصلی")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_economy_menu():
    keyboard = [
        [KeyboardButton("💰 موجودی کیف پول"), KeyboardButton("🎁 هدیه روزانه")],
        [KeyboardButton("💸 انتقال سکه"), KeyboardButton("🏦 وام بانکی")],
        [KeyboardButton("📉 بازپرداخت وام"), KeyboardButton("🏆 برترین‌های ثروت")],
        [KeyboardButton("🔙 بازگشت به منوی اصلی")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_entertainment_menu():
    keyboard = [
        [KeyboardButton("🎮 بازی‌ها"), KeyboardButton("📜 فال حافظ")],
        [KeyboardButton("😂 جوک"), KeyboardButton("💡 دانستنی")],
        [KeyboardButton("❓ معما"), KeyboardButton("📖 داستان")],
        [KeyboardButton("🎯 چالش"), KeyboardButton("🔙 بازگشت به منوی اصلی")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_games_menu():
    keyboard = [
        [KeyboardButton("🎲 تاس"), KeyboardButton("🪙 پرتاب سکه")],
        [KeyboardButton("📝 حدس کلمه"), KeyboardButton("🚩 حدس پرچم")],
        [KeyboardButton("✂️ سنگ کاغذ قیچی"), KeyboardButton("⚔️ دوئل")],
        [KeyboardButton("🔙 بازگشت به سرگرمی")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_utility_menu():
    keyboard = [
        [KeyboardButton("🌐 مترجم"), KeyboardButton("🧮 ماشین حساب")],
        [KeyboardButton("⛅️ هواشناسی"), KeyboardButton("📅 تاریخ و زمان")],
        [KeyboardButton("🔙 بازگشت به منوی اصلی")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_settings_menu():
    keyboard = [
        [KeyboardButton("🤖 تنظیمات هوش مصنوعی")],
        [KeyboardButton("🔙 بازگشت به منوی اصلی")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

from telegram import ReplyKeyboardMarkup, KeyboardButton

def get_main_menu():
    keyboard = [
        [KeyboardButton("🛡 مدیریت"), KeyboardButton("👤 حساب کاربری")],
        [KeyboardButton("🏦 بانک و اقتصاد"), KeyboardButton("🎮 سرگرمی")],
        [KeyboardButton("🛠 کاربردی"), KeyboardButton("🤖 دستیار هوشمند")],
        [KeyboardButton("⚙️ تنظیمات"), KeyboardButton("🤝 پشتیبانی")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_admin_menu():
    keyboard = [
        [KeyboardButton("🔒 قفل‌های گروه"), KeyboardButton("👋 خوشامدگویی")],
        [KeyboardButton("🛡 ضد اسپم"), KeyboardButton("📜 قوانین")],
        [KeyboardButton("👤 مدیریت اعضا"), KeyboardButton("💰 تنظیمات اقتصاد")],
        [KeyboardButton("📊 آمار گروه"), KeyboardButton("🔙 بازگشت به منوی اصلی")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_member_mgmt_menu():
    keyboard = [
        [KeyboardButton("⚠️ اخطارها"), KeyboardButton("🔇 محدودیت‌ها")],
        [KeyboardButton("🚫 مسدودسازی"), KeyboardButton("👤 اطلاعات کاربر")],
        [KeyboardButton("🛡 امنیت"), KeyboardButton("🔙 بازگشت به مدیریت")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_warnings_mgmt_menu():
    keyboard = [
        [KeyboardButton("➕ اخطار کاربر"), KeyboardButton("📋 لیست اخطارها")],
        [KeyboardButton("🗑 حذف آخرین اخطار"), KeyboardButton("🔄 پاک کردن همه اخطارها")],
        [KeyboardButton("🔙 بازگشت به مدیریت اعضا")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_mutes_mgmt_menu():
    keyboard = [
        [KeyboardButton("🔇 سکوت کاربر"), KeyboardButton("⏱ سکوت زمان‌دار")],
        [KeyboardButton("🔊 رفع سکوت"), KeyboardButton("📊 لیست کاربران محدود شده")],
        [KeyboardButton("🔙 بازگشت به مدیریت اعضا")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_bans_mgmt_menu():
    keyboard = [
        [KeyboardButton("🚫 بن کاربر"), KeyboardButton("♻️ رفع بن")],
        [KeyboardButton("👥 بن چند کاربر"), KeyboardButton("📋 لیست بن‌ها")],
        [KeyboardButton("🔙 بازگشت به مدیریت اعضا")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_user_info_mgmt_menu():
    keyboard = [
        [KeyboardButton("🔎 پروفایل کاربر"), KeyboardButton("📈 آمار پیام‌ها")],
        [KeyboardButton("⭐ XP و سطح"), KeyboardButton("💰 موجودی سکه")],
        [KeyboardButton("🔙 بازگشت به مدیریت اعضا")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_security_mgmt_menu():
    keyboard = [
        [KeyboardButton("🆕 جلوگیری از ورود ربات"), KeyboardButton("👤 محدودیت عضو جدید")],
        [KeyboardButton("⏳ تایید عضو جدید"), KeyboardButton("📢 گزارش فعالیت")],
        [KeyboardButton("🔙 بازگشت به مدیریت اعضا")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_group_settings_menu():
    keyboard = [
        [KeyboardButton("👋 خوشامدگویی"), KeyboardButton("📜 قوانین")],
        [KeyboardButton("🔗 ضد لینک"), KeyboardButton("🛡 ضد اسپم")],
        [KeyboardButton("🔒 قفل‌ها"), KeyboardButton("⚙️ تنظیمات عمومی")],
        [KeyboardButton("🔙 بازگشت به مدیریت")]
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
        [KeyboardButton("👤 پروفایل")],
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
        [KeyboardButton("🎭 جرات و حقیقت"), KeyboardButton("🎯 چالش")],
        [KeyboardButton("🔙 بازگشت به منوی اصلی")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_games_menu():
    keyboard = [
        [KeyboardButton("🎲 تاس"), KeyboardButton("🪙 پرتاب سکه")],
        [KeyboardButton("🔢 حدس عدد"), KeyboardButton("📝 حدس کلمه")],
        [KeyboardButton("🚩 حدس پرچم"), KeyboardButton("✂️ سنگ کاغذ قیچی")],
        [KeyboardButton("⚔️ دوئل"), KeyboardButton("🧠 تست هوش")],
        [KeyboardButton("🧩 معمای منطقی"), KeyboardButton("🎲 بازی شانسی روزانه")],
        [KeyboardButton("🏆 مسابقه سرعت پاسخ"), KeyboardButton("🔙 بازگشت به سرگرمی")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_tod_menu():
    keyboard = [
        [KeyboardButton("🎯 جرات"), KeyboardButton("💬 حقیقت")],
        [KeyboardButton("🎲 تصادفی"), KeyboardButton("🤝 پیوستن به بازی")],
        [KeyboardButton("🏁 شروع بازی"), KeyboardButton("🔄 نوبت بعدی")],
        [KeyboardButton("🛑 توقف"), KeyboardButton("🔙 بازگشت به سرگرمی")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_joke_categories_menu():
    keyboard = [
        [KeyboardButton("😂 خنده‌دار"), KeyboardButton("😈 شیطنتی")],
        [KeyboardButton("🧠 هوشمندانه"), KeyboardButton("🤣 کوتاه")],
        [KeyboardButton("🔙 بازگشت به سرگرمی")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_challenge_categories_menu():
    keyboard = [
        [KeyboardButton("🎯 چالش تصادفی"), KeyboardButton("⚡ چالش سخت")],
        [KeyboardButton("😂 چالش خنده‌دار"), KeyboardButton("🧠 چالش ذهنی")],
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

def get_welcome_settings_menu():
    keyboard = [
        [KeyboardButton("🔘 فعال/غیرفعال سازی خوشامدگویی")],
        [KeyboardButton("📝 تغییر متن خوشامدگویی")],
        [KeyboardButton("🔙 بازگشت به مدیریت")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_rules_settings_menu():
    keyboard = [
        [KeyboardButton("🔘 فعال/غیرفعال سازی قوانین")],
        [KeyboardButton("📝 تغییر متن قوانین")],
        [KeyboardButton("🔙 بازگشت به مدیریت")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

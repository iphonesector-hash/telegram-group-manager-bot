from telegram.ext import Application

from bot.handlers.start import start_handler
from bot.handlers.errors import error_handler

from bot.modules.panel import get_panel_handlers
from bot.modules.locks import get_handlers as get_lock_handlers
from bot.modules.welcome import get_welcome_handlers
from bot.modules.antispam import get_antispam_handlers
from bot.modules.profile import get_profile_handlers


BOT_TOKEN = "8819957944:AAFVCeFQ3RXPImvhF3jjL1D418xIg9B9JLs"


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # /start
    app.add_handler(start_handler, group=0)

    # پنل مدیریت (اول اجرا شود)
    for handler in get_panel_handlers():
        app.add_handler(handler, group=0)

    # قفل‌ها (بعد از دستورات)
    for handler in get_lock_handlers():
        app.add_handler(handler, group=1)

    # خوشامدگویی
    for handler in get_welcome_handlers():
        app.add_handler(handler, group=0)

    # ضد اسپم
    for handler in get_antispam_handlers():
        app.add_handler(handler, group=1)

    # پروفایل
    for handler in get_profile_handlers():
        app.add_handler(handler, group=0)

    # خطاها
    app.add_error_handler(error_handler)

    print("ربات روشن شد... منتظر پیام هستم.")

    app.run_polling()


if __name__ == "__main__":
    main()

import sys
import os
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# اضافه کردن مسیر ریشه به sys.path برای کارکرد صحیح importهای bot.xxx
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from bot.database.session import init_db
from bot.handlers.start import start_handler
from bot.handlers.errors import error_handler

from bot.modules.panel import get_panel_handlers
from bot.modules.locks import get_handlers as get_lock_handlers
from bot.modules.welcome import get_welcome_handlers
from bot.modules.antispam import get_antispam_handlers
from bot.modules.profile import get_profile_handlers
from bot.modules.registration import get_registration_handlers
from bot.modules.warnings import get_handlers as get_warning_handlers

# استفاده از متغیر محیطی برای امنیت بیشتر
BOT_TOKEN = os.getenv("BOT_TOKEN", "8819957944:AAFVCeFQ3RXPImvhF3jjL1D418xIg9B9JLs")


def main():
    # Initialize Database
    init_db()

    if BOT_TOKEN == "8819957944:AAFVCeFQ3RXPImvhF3jjL1D418xIg9B9JLs":
        print("⚠️ Warning: Using default bot token. Set BOT_TOKEN environment variable for production.")

    app = Application.builder().token(BOT_TOKEN).build()

    # گروه 0: ثبت‌نام (Registration)
    for handler in get_registration_handlers():
        app.add_handler(handler, group=0)

    # گروه 1: تمام دستورات (Commands)
    app.add_handler(start_handler, group=1)

    for handler in get_panel_handlers():
        app.add_handler(handler, group=1)

    for handler in get_profile_handlers():
        if isinstance(handler, CommandHandler):
            app.add_handler(handler, group=1)
        else:
            app.add_handler(handler, group=5)

    for handler in get_lock_handlers():
        if isinstance(handler, CommandHandler):
            app.add_handler(handler, group=1)
        else:
            app.add_handler(handler, group=4)

    for handler in get_warning_handlers():
        if isinstance(handler, CommandHandler):
            app.add_handler(handler, group=1)
        else:
            # mute_checker
            app.add_handler(handler, group=4)

    # گروه 2: خوشامدگویی
    for handler in get_welcome_handlers():
        app.add_handler(handler, group=2)

    # گروه 3: ضد اسپم
    for handler in get_antispam_handlers():
        app.add_handler(handler, group=3)

    # خطاها
    app.add_error_handler(error_handler)

    print("ربات SectorBot روشن شد... منتظر پیام هستم.")

    app.run_polling()


if __name__ == "__main__":
    main()

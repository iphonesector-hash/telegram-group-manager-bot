import sys
import os
from dotenv import load_dotenv

# مسیر اصلی پروژه
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

# خواندن .env از ریشه پروژه
load_dotenv(os.path.join(BASE_DIR, ".env"))

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters
)

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
from bot.modules.rules import get_rules_handlers
from bot.modules.economy import get_handlers as get_economy_handlers
from bot.modules.entertainment import get_handlers as get_entertainment_handlers


BOT_TOKEN = os.getenv("BOT_TOKEN")


def main():

    if not BOT_TOKEN:
        print("❌ BOT_TOKEN پیدا نشد. فایل .env را چک کنید.")
        return

    # دیتابیس
    init_db()

    app = Application.builder().token(BOT_TOKEN).build()


    # گروه 0 - ثبت کاربران (Middleware)
    for handler in get_registration_handlers():
        app.add_handler(handler, group=0)

    # گروه 1 - فیلترهای مسدودکننده (Mute & Antispam)
    # این‌ها باید قبل از دستورات باشند تا کاربران محدود شده نتوانند از دستورات استفاده کنند
    for handler in get_warning_handlers():
        if not isinstance(handler, CommandHandler):
            app.add_handler(handler, group=1)

    for handler in get_antispam_handlers():
        if not isinstance(handler, CommandHandler):
            app.add_handler(handler, group=1)


    # گروه 2 - دستورات (Commands)
    app.add_handler(start_handler, group=2)

    for handler in get_panel_handlers():
        app.add_handler(handler, group=2)

    for handler in get_profile_handlers():
        if isinstance(handler, CommandHandler):
            app.add_handler(handler, group=2)

    for handler in get_lock_handlers():
        if isinstance(handler, CommandHandler):
            app.add_handler(handler, group=2)

    for handler in get_warning_handlers():
        if isinstance(handler, CommandHandler):
            app.add_handler(handler, group=2)

    for handler in get_rules_handlers():
        app.add_handler(handler, group=2)

    for handler in get_welcome_handlers():
        if isinstance(handler, CommandHandler):
            app.add_handler(handler, group=2)

    for handler in get_antispam_handlers():
        if isinstance(handler, CommandHandler):
            app.add_handler(handler, group=2)

    for handler in get_economy_handlers():
        app.add_handler(handler, group=2)

    for handler in get_entertainment_handlers():
        app.add_handler(handler, group=2)


    # گروه 3 - خوش آمدگویی (پیام‌های سیستمی)
    for handler in get_welcome_handlers():
        if not isinstance(handler, CommandHandler):
            app.add_handler(handler, group=3)


    # گروه 4 - قفل‌های محتوا (حذف پیام‌های غیرمجاز)
    for handler in get_lock_handlers():
        if not isinstance(handler, CommandHandler):
            app.add_handler(handler, group=4)


    # گروه 5 - آمار و اقتصاد (XP/Coins)
    for handler in get_profile_handlers():
        if not isinstance(handler, CommandHandler):
            app.add_handler(handler, group=5)


    app.add_error_handler(error_handler)


    print("✅ ربات SectorBot با موفقیت روشن شد و آماده به کار است.")

    app.run_polling()



if __name__ == "__main__":
    main()

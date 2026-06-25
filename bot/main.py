import sys
import os
from dotenv import load_dotenv

load_dotenv()

from telegram.ext import (
    Application,
    CommandHandler,
)

# اضافه کردن مسیر ریشه برای import ها
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


BOT_TOKEN = os.getenv("BOT_TOKEN")


def main():

    if not BOT_TOKEN:
        print("❌ BOT_TOKEN پیدا نشد. فایل .env را چک کن.")
        return


    init_db()


    app = Application.builder().token(BOT_TOKEN).build()


    # گروه 0: ثبت نام کاربر
    for handler in get_registration_handlers():
        app.add_handler(handler, group=0)


    # گروه 1: دستورات
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



    # خوشامد
    for handler in get_welcome_handlers():
        app.add_handler(handler, group=2)


    # ضد اسپم
    for handler in get_antispam_handlers():
        app.add_handler(handler, group=3)



    app.add_error_handler(error_handler)


    print("✅ SectorBot روشن شد... منتظر پیام هستم.")


    app.run_polling()



if __name__ == "__main__":
    main()

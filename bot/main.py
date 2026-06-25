import sys
import os
from telegram.ext import Application, CommandHandler

# اضافه کردن مسیر ریشه به sys.path برای کارکرد صحیح importهای bot.xxx
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from bot.handlers.start import start_handler
from bot.handlers.errors import error_handler

from bot.modules.panel import get_panel_handlers
from bot.modules.locks import get_handlers as get_lock_handlers
from bot.modules.welcome import get_welcome_handlers
from bot.modules.antispam import get_antispam_handlers
from bot.modules.profile import get_profile_handlers

# استفاده از متغیر محیطی برای امنیت بیشتر
BOT_TOKEN = os.getenv("BOT_TOKEN", "8819957944:AAFVCeFQ3RXPImvhF3jjL1D418xIg9B9JLs")


def main():
    if BOT_TOKEN == "8819957944:AAFVCeFQ3RXPImvhF3jjL1D418xIg9B9JLs":
        print("⚠️ Warning: Using default bot token. Set BOT_TOKEN environment variable for production.")

    app = Application.builder().token(BOT_TOKEN).build()

    # گروه 0: تمام دستورات (Commands)
    # دستورات باید در بالاترین اولویت باشند تا توسط فیلترهای کلی مسدود نشوند
    app.add_handler(start_handler, group=0)

    for handler in get_panel_handlers():
        app.add_handler(handler, group=0)

    # جدا کردن دستورات از فیلترهای کلی در سایر ماژول‌ها

    # پروفایل (دستورات در گروه 0، شمارنده در گروه 4)
    for handler in get_profile_handlers():
        if isinstance(handler, CommandHandler):
            app.add_handler(handler, group=0)
        else:
            app.add_handler(handler, group=4)

    # قفل‌ها (دستورات در گروه 0، فیلتر در گروه 3)
    for handler in get_lock_handlers():
        if isinstance(handler, CommandHandler):
            app.add_handler(handler, group=0)
        else:
            app.add_handler(handler, group=3)

    # خوشامدگویی (گروه 1)
    for handler in get_welcome_handlers():
        app.add_handler(handler, group=1)

    # ضد اسپم (گروه 2)
    for handler in get_antispam_handlers():
        app.add_handler(handler, group=2)

    # خطاها
    app.add_error_handler(error_handler)

    print("ربات روشن شد... منتظر پیام هستم.")

    app.run_polling()


if __name__ == "__main__":
    main()

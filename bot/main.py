import sys
import os
from dotenv import load_dotenv
from telegram import WebAppInfo, MenuButtonWebApp
from telegram.ext import Application, CommandHandler

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
load_dotenv(os.path.join(BASE_DIR, ".env"))

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
from bot.modules.games import get_handlers as get_game_handlers
from bot.modules.ai import get_handlers as get_ai_handlers
from bot.modules.extra import get_extra_handlers
from bot.modules.sector_pet import get_handlers as get_sector_pet_handlers

BOT_TOKEN = os.getenv("BOT_TOKEN")
MINI_APP_URL = os.getenv("MINI_APP_URL", "https://isectorland-miniapp.vercel.app").split("?", 1)[0] + "?v=20260823-3"


async def setup_telegram_ui(app: Application):
    """Register the Mini App as the default private-chat menu button.

    This makes the Telegram-native WebApp launcher available without requiring
    each user to run /start first. Per-chat /start setup remains as a fallback.
    """
    try:
        await app.bot.set_chat_menu_button(
            menu_button=MenuButtonWebApp(
                text="🚀 SectorLand",
                web_app=WebAppInfo(url=MINI_APP_URL),
            )
        )
        print("✅ Default SectorLand Mini App menu button registered.")
    except Exception as exc:
        print(f"⚠️ Could not register default Mini App menu button: {exc}")


def build_application() -> Application:
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN is not configured")

    init_db()
    app = Application.builder().token(BOT_TOKEN).post_init(setup_telegram_ui).build()

    for h in get_registration_handlers(): app.add_handler(h, group=0)
    for h in get_warning_handlers():
        if not isinstance(h, CommandHandler): app.add_handler(h, group=1)
    for h in get_antispam_handlers():
        if not isinstance(h, CommandHandler): app.add_handler(h, group=1)

    app.add_handler(start_handler, group=2)
    for h in get_sector_pet_handlers(): app.add_handler(h, group=2)
    for h in get_panel_handlers(): app.add_handler(h, group=2)
    for h in get_economy_handlers(): app.add_handler(h, group=2)
    for h in get_profile_handlers():
        if isinstance(h, CommandHandler) or (hasattr(h, "filters") and "TEXT" in str(h.filters)): app.add_handler(h, group=2)
    for h in get_entertainment_handlers(): app.add_handler(h, group=2)
    for h in get_lock_handlers():
        if isinstance(h, CommandHandler) or (hasattr(h, "filters") and "TEXT" in str(h.filters)): app.add_handler(h, group=2)
    for h in get_warning_handlers():
        if isinstance(h, CommandHandler): app.add_handler(h, group=2)
    for h in get_rules_handlers(): app.add_handler(h, group=2)
    for h in get_welcome_handlers():
        if isinstance(h, CommandHandler) or (hasattr(h, "filters") and "TEXT" in str(h.filters)): app.add_handler(h, group=2)
    for h in get_antispam_handlers():
        if isinstance(h, CommandHandler) or (hasattr(h, "filters") and "TEXT" in str(h.filters)): app.add_handler(h, group=2)
    for h in get_extra_handlers(): app.add_handler(h, group=2)
    for h in get_game_handlers(): app.add_handler(h, group=2)
    for h in get_ai_handlers(): app.add_handler(h, group=3)
    for h in get_welcome_handlers():
        if not isinstance(h, CommandHandler) and not (hasattr(h, "filters") and "TEXT" in str(h.filters)): app.add_handler(h, group=4)
    for h in get_lock_handlers():
        if not isinstance(h, CommandHandler) and not (hasattr(h, "filters") and "TEXT" in str(h.filters)): app.add_handler(h, group=4)
    for h in get_profile_handlers():
        if not isinstance(h, CommandHandler) and not (hasattr(h, "filters") and "TEXT" in str(h.filters)): app.add_handler(h, group=5)

    app.add_error_handler(error_handler)
    return app


def main():
    app = build_application()
    print("✅ iSectorLand unified bot started in polling mode.")
    app.run_polling(allowed_updates=None)


if __name__ == "__main__":
    main()

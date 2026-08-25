import sys
import os
from dotenv import load_dotenv
from telegram import WebAppInfo, MenuButtonWebApp
from telegram.ext import Application, CommandHandler, MessageHandler, filters

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
load_dotenv(os.path.join(BASE_DIR, ".env"))

from bot.services import sector_economy  # noqa: F401
from bot.database.session import init_db
from bot.handlers.start import start_handler
from bot.handlers.errors import error_handler
from bot.modules.release_announcements import get_handlers as get_release_announcement_handlers
from bot.modules.required_membership import get_handlers as get_required_membership_handlers
from bot.modules.panel import get_panel_handlers
from bot.modules.locks import get_handlers as get_lock_handlers
from bot.modules.welcome import get_welcome_handlers
from bot.modules.antispam import get_handlers as get_antispam_handlers
from bot.modules.profile import get_profile_handlers
from bot.modules.registration import get_registration_handlers
from bot.modules.warnings import get_handlers as get_warning_handlers
from bot.modules.rules import get_rules_handlers
from bot.modules.economy import get_handlers as get_economy_handlers
from bot.modules.entertainment import get_handlers as get_entertainment_handlers
from bot.modules.games import get_handlers as get_game_handlers
from bot.modules.ai import get_handlers as get_ai_handlers
from bot.modules.extra import get_extra_handlers
from bot.modules.sector_emoji_library import get_handlers as get_sector_emoji_library_handlers
from bot.modules.sector_synced_actions import get_handlers as get_sector_synced_action_handlers
import bot.modules.sector_pet as sector_pet_module
from bot.modules.sector_pet import get_handlers as get_sector_pet_handlers, sector_command
from bot.modules.sector_social import get_handlers as get_sector_social_handlers
from bot.modules.stickers import get_handlers as get_sticker_handlers
from bot.utils.animated_emoji import get_sector_emoji_ids

# Sector chat text and inline buttons share one cached Premium-emoji lookup.
# This replaces the old per-icon database reads without changing old handlers.
sector_pet_module.sector_emoji_ids = get_sector_emoji_ids

BOT_TOKEN = os.getenv("BOT_TOKEN")
MINI_APP_URL = os.getenv("MINI_APP_URL", "https://isectorland-miniapp.vercel.app").split("?", 1)[0]
MAIN_MENU_PATTERN = r"^(?:🛡 مدیریت|👤 حساب کاربری|🏦 بانک و اقتصاد|🎮 سرگرمی|🛠 کاربردی|🤖 دستیار هوشمند|🤖 سکتور کوچولو|سکتور کوچولو|⚙️ تنظیمات|🤝 پشتیبانی|🔙 بازگشت به منوی اصلی)$"


async def sector_menu_entry(update, context):
    """Make the persistent chat button open the exact same Sector panel."""
    context.user_data.pop("sector_pending", None)
    context.user_data.pop("sector_selected_target", None)
    await sector_command(update, context)


async def reset_sector_pending_for_main_menu(update, context):
    """Do not let a stale rename/talk flow consume persistent menu buttons."""
    context.user_data.pop("sector_pending", None)
    context.user_data.pop("sector_selected_target", None)


async def setup_telegram_ui(app: Application):
    try:
        await app.bot.set_chat_menu_button(menu_button=MenuButtonWebApp(text="sector", web_app=WebAppInfo(url=MINI_APP_URL)))
        print("✅ Default SectorLand Mini App menu button registered.")
    except Exception as exc:
        print(f"⚠️ Could not register default Mini App menu button: {exc}")


def build_application(*, initialize_database: bool = True) -> Application:
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN is not configured")

    if initialize_database:
        init_db()
    app = Application.builder().token(BOT_TOKEN).post_init(setup_telegram_ui).build()

    for h in get_release_announcement_handlers(): app.add_handler(h, group=-20)
    for h in get_required_membership_handlers(): app.add_handler(h, group=-10)
    for h in get_sticker_handlers(): app.add_handler(h, group=-5)
    for h in get_sector_emoji_library_handlers(): app.add_handler(h, group=-4)
    for h in get_sector_synced_action_handlers(): app.add_handler(h, group=-3)

    # Persistent composer buttons must win over stale Sector ForceReply flows.
    app.add_handler(MessageHandler(filters.Regex(r"^(?:🤖 سکتور کوچولو|سکتور کوچولو)$"), sector_menu_entry), group=-3)
    app.add_handler(MessageHandler(filters.Regex(MAIN_MENU_PATTERN), reset_sector_pending_for_main_menu), group=-2)

    for h in get_registration_handlers(): app.add_handler(h, group=0)
    for h in get_sector_social_handlers(): app.add_handler(h, group=1)
    for h in get_warning_handlers():
        if not isinstance(h, CommandHandler): app.add_handler(h, group=1)
    for h in get_antispam_handlers():
        if not isinstance(h, CommandHandler): app.add_handler(h, group=1)

    app.add_handler(start_handler, group=2)
    for h in get_sector_pet_handlers():
        app.add_handler(h, group=-1 if getattr(h.callback, "__name__", "") == "pending_text" else 2)
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

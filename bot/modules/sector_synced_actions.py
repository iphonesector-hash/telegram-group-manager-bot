"""High-priority Sector care callbacks that keep Telegram chat and Mini App state coherent."""
from telegram import Update
from telegram.ext import ApplicationHandlerStop, CallbackQueryHandler, ContextTypes

from bot.database.session import get_session
from bot.modules.sector_pet import pet_keyboard, pet_text, show_panel
from bot.services import sector_pet as legacy
from bot.services import sector_story


async def synced_sector_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = str(query.data or "")
    if not data.startswith("sector_action:"):
        return
    action = data.split(":", 1)[1]
    session = get_session()
    try:
        result = legacy.perform_action(session, query.from_user.id, action)
        if result.get("status") != "success":
            session.rollback()
            await query.answer(result.get("message") or "این کار انجام نشد.", show_alert=True)
            raise ApplicationHandlerStop()

        pet_obj = legacy.get_or_create_pet(session, query.from_user.id)
        snapshot = sector_story.snapshot(session, query.from_user.id, pet_obj)
        advanced = False
        next_objective = ""
        if snapshot.get("scene", {}).get("ready"):
            advanced_result = sector_story.advance(session, query.from_user.id)
            advanced = advanced_result.get("status") == "success"
            if advanced:
                pet_obj = legacy.get_or_create_pet(session, query.from_user.id)
                next_snapshot = sector_story.snapshot(session, query.from_user.id, pet_obj)
                next_objective = next_snapshot.get("scene", {}).get("objective") or ""

        pet = legacy.serialize_pet(pet_obj)
        daily = legacy.daily_progress(session, query.from_user.id)
        session.commit()
        await query.answer("هدف داستان هم کامل شد" if advanced else "انجام شد")
        text = pet_text(pet, daily)
        if advanced:
            text += "\n\n📖 <b>داستان جلو رفت.</b>\n" + (f"قدم بعدی: {next_objective}" if next_objective else "مرحله بعدی آماده است.")
        await show_panel(query, text, pet_keyboard(query.from_user.id))
    except ApplicationHandlerStop:
        raise
    except Exception:
        session.rollback()
        try:
            await query.answer("عملیات انجام نشد؛ دوباره تلاش کن.", show_alert=True)
        except Exception:
            pass
        raise
    finally:
        session.close()
    raise ApplicationHandlerStop()


def get_handlers():
    return [CallbackQueryHandler(synced_sector_action, pattern=r"^sector_action:")]

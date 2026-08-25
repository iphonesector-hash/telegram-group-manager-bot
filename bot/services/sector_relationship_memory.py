"""Add relationship and journey context to Sector chat memory."""
from bot.services import sector_meta, sector_v2
from bot.services import sector_pet as legacy

_ORIGINAL_CHAT_CONTEXT = sector_v2.chat_context


def relationship_chat_context(session, user_id, limit=8):
    base = _ORIGINAL_CHAT_CONTEXT(session, user_id, limit=limit)
    pet = legacy.get_or_create_pet(session, user_id)
    bond = sector_meta.bond_rows(session, user_id, limit=1)
    notes = [
        f"الان در فصل {int(pet.story_chapter or 1)} و صحنه {int(pet.story_progress or 0)+1} سفر هستیم.",
        f"تا امروز {int(pet.total_care_days or 0)} روز مراقبت و زنجیره {int(pet.streak_days or 0)} روزه داریم.",
        f"شخصیت فعلی من {pet.personality or 'کنجکاو'} و مسیر تکامل من {pet.evolution_path or 'هنوز انتخاب نشده'} است.",
    ]
    if bond:
        top = bond[0]
        notes.append(f"نزدیک‌ترین پیوند اجتماعی فعلی با {top.get('name','یک دوست')} در سطح {top.get('level',1)} است.")
    return (base + " | " + " | ".join(notes))[:2600]


sector_v2.chat_context = relationship_chat_context

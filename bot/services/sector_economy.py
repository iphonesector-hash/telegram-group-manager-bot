"""Sector social economy and extended cosmetic catalog.

Loaded by bot.main so the unified Vercel runtime and polling runtime share the
same catalog and social rewards without a schema migration.
"""
import datetime
import random

from bot.database.models import SectorPetSocial, User
from bot.services import sector_pet
from bot.utils.helpers import OWNER_ID

EXTRA_COSMETICS = {
    "midnight_shell": {"title": "بدنه نیمه‌شب", "icon": "🌑", "cost": 1800, "slot": "body", "rarity": "rare", "description": "بدنه تیره با حال‌وهوای فضایی"},
    "galaxy_shell": {"title": "بدنه کهکشانی", "icon": "🌌", "cost": 5000, "slot": "body", "rarity": "legendary", "description": "بدنه افسانه‌ای برای کلکسیونرها"},
    "neon_cap": {"title": "کلاه نئونی", "icon": "🧢", "cost": 850, "slot": "head", "rarity": "common", "description": "کلاه سبک برای روزهای آرکید"},
    "sector_crown": {"title": "تاج سکتور", "icon": "👑", "cost": 4500, "slot": "head", "rarity": "legendary", "description": "تاج مخصوص قهرمان‌های SectorLand"},
    "wizard_hat": {"title": "کلاه نابغه", "icon": "🧙", "cost": 2800, "slot": "head", "rarity": "epic", "description": "برای سکتورهای عاشق یادگیری"},
    "cyber_glasses": {"title": "عینک سایبری", "icon": "🕶️", "cost": 900, "slot": "face", "rarity": "rare", "description": "استایل سایبری برای صورت"},
    "heart_visor": {"title": "ویزور قلبی", "icon": "💖", "cost": 1500, "slot": "face", "rarity": "epic", "description": "ویزور مخصوص همراه‌های صمیمی"},
    "jetpack": {"title": "جت‌پک", "icon": "🚀", "cost": 4200, "slot": "back", "rarity": "legendary", "description": "برای سکتورهای ماجراجو"},
    "mini_cape": {"title": "شنل قهرمانی", "icon": "🦸", "cost": 1600, "slot": "back", "rarity": "rare", "description": "شنل سبک قهرمان‌های کوچک"},
    "game_pad": {"title": "گیم‌پد", "icon": "🎮", "cost": 1300, "slot": "hand", "rarity": "rare", "description": "برای سکتورهای گیمر"},
    "sector_flower": {"title": "گل سکتور", "icon": "🌷", "cost": 600, "slot": "hand", "rarity": "common", "description": "هدیه ساده و دوست‌داشتنی"},
    "star_aura": {"title": "هاله ستاره‌ای", "icon": "✨", "cost": 2200, "slot": "aura", "rarity": "epic", "description": "هاله درخشان اطراف سکتور"},
    "galaxy_aura": {"title": "هاله کهکشانی", "icon": "💫", "cost": 6000, "slot": "aura", "rarity": "mythic", "description": "کمیاب‌ترین هاله فعلی"},
    "moon_room": {"title": "پس‌زمینه ماه", "icon": "🌙", "cost": 2400, "slot": "background", "rarity": "epic", "description": "پس‌زمینه آرام ماه"},
    "arcade_bg": {"title": "پس‌زمینه آرکید", "icon": "🕹️", "cost": 3000, "slot": "background", "rarity": "epic", "description": "اتاق آرکیدی پرانرژی"},
}

_BASE_META = {
    "blue_shell": ("common", "بدنه کلاسیک آبی"),
    "gold_shell": ("epic", "بدنه طلایی درخشان"),
    "captain_hat": ("rare", "کلاه فرماندهی Sector"),
    "neon_wings": ("epic", "بال‌های نئونی"),
    "plasma_tool": ("epic", "ابزار پلاسمایی"),
}
for _key, (_rarity, _description) in _BASE_META.items():
    if _key in sector_pet.COSMETICS:
        sector_pet.COSMETICS[_key].setdefault("rarity", _rarity)
        sector_pet.COSMETICS[_key].setdefault("description", _description)
sector_pet.COSMETICS.update(EXTRA_COSMETICS)


def appearance_icons(pet):
    """Return compact equipped-item metadata for cards and Telegram messages."""
    appearance = dict(getattr(pet, "appearance", None) or {})
    result = []
    for slot, item_key in appearance.items():
        item = sector_pet.COSMETICS.get(item_key)
        if item:
            result.append({"slot": slot, "key": item_key, **item})
    return result


def social_action_v2(session, actor_id: int, target_id: int, action: str):
    """Social action with conservative coin rewards and one-use-per-pair/day guard."""
    if actor_id == target_id:
        return {"status": "error", "message": "این کار را نمی‌توانی با خودت انجام بدهی."}
    if action not in ("visit", "gift", "battle"):
        return {"status": "error", "message": "تعامل نامعتبر است."}

    ids = sorted({int(actor_id), int(target_id)})
    rows = session.query(User).filter(User.id.in_(ids)).order_by(User.id).with_for_update().all()
    users = {int(row.id): row for row in rows}
    actor, target = users.get(int(actor_id)), users.get(int(target_id))
    if not actor or not target:
        return {"status": "error", "message": "هر دو کاربر باید قبلاً /start را زده باشند."}

    day = datetime.datetime.utcnow().strftime("%Y%m%d")
    exists = session.query(SectorPetSocial.id).filter_by(actor_id=actor_id, target_id=target_id, action=action, day_key=day).first()
    if exists:
        return {"status": "error", "message": "این تعامل با این کاربر امروز قبلاً انجام شده."}

    actor_pet = sector_pet.get_or_create_pet(session, actor_id, lock=True)
    target_pet = sector_pet.get_or_create_pet(session, target_id, lock=True)
    reward_xp = 0
    reward_coins = 0
    won = None

    if action == "gift":
        if actor_id != OWNER_ID and int(actor.coins or 0) < 50:
            return {"status": "error", "message": "برای هدیه ۵۰ سکه لازم داری."}
        if actor_id != OWNER_ID:
            actor.coins = int(actor.coins or 0) - 50
        target.coins = int(target.coins or 0) + 50
        target_pet.happiness = min(100, int(target_pet.happiness or 0) + 10)
        reward_xp = 5
        actor_pet.xp = int(actor_pet.xp or 0) + reward_xp
        message = "🎁 هدیه ۵۰ سکه‌ای فرستاده شد."
    elif action == "battle":
        attack = sector_pet.level_from_xp(actor_pet.xp) + int(actor_pet.knowledge or 0) // 10 + random.randint(1, 12)
        defense = sector_pet.level_from_xp(target_pet.xp) + int(target_pet.health or 0) // 10 + random.randint(1, 12)
        won = attack >= defense
        reward_xp = 45 if won else 12
        reward_coins = 25 if won else 0
        actor_pet.xp = int(actor_pet.xp or 0) + reward_xp
        actor_pet.happiness = min(100, int(actor_pet.happiness or 0) + (7 if won else 2))
        if actor_id != OWNER_ID and reward_coins:
            actor.coins = int(actor.coins or 0) + reward_coins
        message = f"⚔️ نبرد را بردی! +{reward_xp} XP و +{reward_coins} سکه" if won else f"⚔️ این نبرد را باختی؛ اما +{reward_xp} XP گرفتی."
    else:
        reward_xp = 20
        reward_coins = 8
        actor_pet.happiness = min(100, int(actor_pet.happiness or 0) + 5)
        actor_pet.xp = int(actor_pet.xp or 0) + reward_xp
        if actor_id != OWNER_ID:
            actor.coins = int(actor.coins or 0) + reward_coins
        message = f"🏠 به اتاق {target_pet.name} سر زدی! +{reward_xp} XP و +{reward_coins} سکه"

    session.add(SectorPetSocial(actor_id=actor_id, target_id=target_id, action=action, day_key=day, payload={"reward_xp": reward_xp, "reward_coins": reward_coins, "won": won}))
    return {
        "status": "success", "action": action, "message": message,
        "coins": int(actor.coins or 0), "reward_xp": reward_xp,
        "reward_coins": reward_coins, "won": won,
        "pet": sector_pet.serialize_pet(actor_pet),
        "target_pet": sector_pet.serialize_pet(target_pet),
    }


sector_pet.social_action = social_action_v2

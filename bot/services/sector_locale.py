"""Persian display labels for Sector data without changing technical keys."""
from bot.services import sector_meta, sector_v2

_STAGE_TITLES = {
    "scrap": "واحد فرسوده",
    "patched": "واحد بازسازی‌شده",
    "core": "واحد هسته",
    "advanced": "سکتور پیشرفته",
    "elite": "سکتور نخبه",
    "mythic": "سکتور اسطوره‌ای",
}

RARITY_LABELS = {
    "common": "معمولی",
    "rare": "کمیاب",
    "epic": "حماسی",
    "legendary": "افسانه‌ای",
    "mythic": "اسطوره‌ای",
}

_BOSS_TITLES = {
    "VOID WARDEN": "نگهبان خلأ",
}

_original_boss_snapshot = sector_meta.boss_snapshot
_original_attack_boss = sector_meta.attack_boss


def _localized_boss_snapshot(*args, **kwargs):
    data = _original_boss_snapshot(*args, **kwargs)
    data = dict(data or {})
    data["title"] = _BOSS_TITLES.get(str(data.get("title") or ""), data.get("title"))
    return data


def _localized_attack_boss(*args, **kwargs):
    data = _original_attack_boss(*args, **kwargs)
    if isinstance(data, dict):
        data = dict(data)
        data["message"] = str(data.get("message") or "").replace(" Damage", " آسیب").replace("Boss", "باس")
        if isinstance(data.get("boss"), dict):
            boss = dict(data["boss"])
            boss["title"] = _BOSS_TITLES.get(str(boss.get("title") or ""), boss.get("title"))
            data["boss"] = boss
    return data


def apply_sector_locale():
    for stage in getattr(sector_v2, "VISUAL_STAGES", []):
        stage_id = str(stage.get("id") or "")
        if stage_id in _STAGE_TITLES:
            stage["title"] = _STAGE_TITLES[stage_id]
    for item in getattr(sector_v2, "CATALOG", {}).values():
        item["rarity_label"] = RARITY_LABELS.get(str(item.get("rarity") or ""), str(item.get("rarity") or ""))
    quests = getattr(sector_meta, "QUEST_DEFS", {})
    if "bond_link" in quests:
        quests["bond_link"]["hint"] = "با یک کاربر به سطح پیوند ۲ برس"
    if "boss_hunter" in quests:
        quests["boss_hunter"]["title"] = "شکارچی خلأ"
        quests["boss_hunter"]["hint"] = "۵۰۰ آسیب به باس وارد کن"
    sector_meta.boss_snapshot = _localized_boss_snapshot
    sector_meta.attack_boss = _localized_attack_boss


apply_sector_locale()

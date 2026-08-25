"""Persian display labels for Sector data without changing technical keys."""
from bot.services import sector_v2

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


def apply_sector_locale():
    for stage in getattr(sector_v2, "VISUAL_STAGES", []):
        stage_id = str(stage.get("id") or "")
        if stage_id in _STAGE_TITLES:
            stage["title"] = _STAGE_TITLES[stage_id]
    # Keep rarity machine values untouched; expose a separate Persian label.
    for item in getattr(sector_v2, "CATALOG", {}).values():
        item["rarity_label"] = RARITY_LABELS.get(str(item.get("rarity") or ""), str(item.get("rarity") or ""))


apply_sector_locale()

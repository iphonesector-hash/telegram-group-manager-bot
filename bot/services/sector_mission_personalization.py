"""Stable behavior-aware mission selection for Sector Koochooloo."""
import datetime

from bot.services import sector_meta

_ORIGINAL = sector_meta.mission_snapshot


def _history_scores(session, user_id, now):
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    start = today_start - datetime.timedelta(days=7)
    return {
        metric: sector_meta._metric(session, user_id, metric, start, today_start)
        for metric in ("care", "game", "social", "chat", "shop", "memory_game")
    }


def personalized_mission_snapshot(session, user_id, now=None):
    now = now or sector_meta.utcnow()
    missions = _ORIGINAL(session, user_id, now)
    by_id = {m["id"]: m for m in missions}
    scores = _history_scores(session, user_id, now)

    # Keep one predictable care mission, then choose two of the three lifestyle
    # lanes. With no history, rotate deterministically by user/date.
    daily_candidates = [
        ("daily_game", scores["game"]),
        ("daily_social", scores["social"]),
        ("daily_chat", scores["chat"]),
    ]
    if not any(score for _, score in daily_candidates):
        seed = int(user_id) + int(now.strftime("%Y%m%d"))
        daily_candidates = daily_candidates[seed % 3:] + daily_candidates[:seed % 3]
    else:
        daily_candidates.sort(key=lambda item: (item[1], item[0]), reverse=True)

    weekly_candidates = [
        ("weekly_memory", scores["game"] + scores["memory_game"] * 2),
        ("weekly_shop", scores["shop"] + scores["care"] // 4),
    ]
    weekly_candidates.sort(key=lambda item: (item[1], item[0]), reverse=True)

    chosen = ["daily_care"] + [key for key, _ in daily_candidates[:2]] + [weekly_candidates[0][0]]
    reason_map = {
        "daily_care": "مسیر پایه مراقبت روزانه",
        "daily_game": "بر اساس علاقه اخیر به بازی‌ها",
        "daily_social": "بر اساس تعامل‌های اجتماعی اخیر",
        "daily_chat": "بر اساس گفت‌وگوهای اخیر با سکتور",
        "weekly_memory": "بر اساس فعالیت بازی و حافظه",
        "weekly_shop": "بر اساس رشد تجهیزات و اقتصاد",
    }
    result = []
    for key in chosen:
        mission = by_id.get(key)
        if not mission:
            continue
        mission = dict(mission)
        mission["personalized"] = True
        mission["why"] = reason_map.get(key, "مأموریت پیشنهادی")
        result.append(mission)
    return result


sector_meta.mission_snapshot = personalized_mission_snapshot

import json
import logging
import os
from pathlib import Path

from bot.database.models import AppSetting
from bot.database.session import get_session

LOGGER = logging.getLogger(__name__)
BASE_DIR = Path(__file__).resolve().parents[2]
MANIFEST_PATH = BASE_DIR / "release" / "current.json"
DEFAULT_CHANNEL = os.getenv("SECTOR_RELEASE_CHANNEL", "@sectorlandS")
DEFAULT_MINI_APP_URL = os.getenv("MINI_APP_URL", "https://isectorland-miniapp.vercel.app").rstrip("/")
SETTING_KEY = "sector_release_publisher"


def load_release_manifest():
    if not MANIFEST_PATH.exists():
        return None
    try:
        payload = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    except Exception as exc:
        LOGGER.warning("Unable to read release manifest: %s", exc)
        return None
    if not payload.get("release_id") or not payload.get("title"):
        LOGGER.warning("Release manifest is missing release_id/title")
        return None
    return payload


def _get_state(session):
    row = session.query(AppSetting).filter(AppSetting.key == SETTING_KEY).one_or_none()
    if row is None:
        return {}, None
    return dict(row.value or {}), row


def _build_photo_url(manifest):
    image = str(manifest.get("image") or "/assets/sector/brand-hero.svg")
    if image.startswith("https://") or image.startswith("http://"):
        return image
    if not image.startswith("/"):
        image = "/" + image
    return DEFAULT_MINI_APP_URL + image


def _build_caption(manifest):
    title = str(manifest.get("title") or "آپدیت سکتور کوچولو")
    version = str(manifest.get("version") or "")
    summary = str(manifest.get("summary") or "")
    parts = ["🤖 <b>" + title + "</b>"]
    if version:
        parts.append("نسخه: <code>" + version + "</code>")
    if summary:
        parts.append(summary)
    parts.append("\n📣 کانال رسمی آموزش و آپدیت‌های سکتور کوچولو")
    return "\n".join(parts)[:1000]


def _build_details(manifest):
    features = [str(x) for x in manifest.get("features", []) if str(x).strip()]
    usage = [str(x) for x in manifest.get("usage", []) if str(x).strip()]
    lines = ["✨ <b>امکانات جدید</b>"]
    if features:
        lines.extend("• " + item for item in features)
    else:
        lines.append("• بهبودهای جدید سکتور کوچولو")
    if usage:
        lines.append("\n🧭 <b>نحوه استفاده</b>")
        for index, item in enumerate(usage, 1):
            lines.append(str(index) + ". " + item)
    lines.append("\n💡 برای استفاده از ربات، عضویت در @sectorland الزامی است.")
    lines.append("📱 Mini App را از دکمه <b>sector</b> داخل ربات باز کن.")
    lines.append("\n📢 @sectorlandS")
    return "\n".join(lines)[:3900]


async def maybe_publish_current_release(bot, force=False):
    """Publish release/current.json to @sectorlandS once per release_id.

    If Telegram cannot fetch/send the release image, the same announcement is
    delivered as a text-only post so a release is never silently lost.
    """
    manifest = load_release_manifest()
    if not manifest:
        return {"ok": False, "reason": "manifest_missing"}

    release_id = str(manifest["release_id"])
    channel = str(manifest.get("channel") or DEFAULT_CHANNEL)
    session = get_session()
    try:
        state, row = _get_state(session)
        if not force and state.get("last_release_id") == release_id:
            return {"ok": True, "published": False, "reason": "already_published", "release_id": release_id}

        caption = _build_caption(manifest)
        details = _build_details(manifest)
        photo_message_id = None
        details_message_id = None
        fallback_text = False
        photo_error = ""

        try:
            photo_message = await bot.send_photo(
                chat_id=channel,
                photo=_build_photo_url(manifest),
                caption=caption,
                parse_mode="HTML",
            )
            photo_message_id = photo_message.message_id
        except Exception as exc:
            fallback_text = True
            photo_error = f"{type(exc).__name__}: {exc}"[:180]
            LOGGER.warning("Release image failed; using text fallback: %s", photo_error)

        if fallback_text:
            fallback_message = await bot.send_message(
                chat_id=channel,
                text=(caption + "\n\n" + details)[:4000],
                parse_mode="HTML",
                disable_web_page_preview=True,
            )
            details_message_id = fallback_message.message_id
        else:
            details_message = await bot.send_message(
                chat_id=channel,
                text=details,
                parse_mode="HTML",
                disable_web_page_preview=True,
            )
            details_message_id = details_message.message_id

        new_state = {
            "last_release_id": release_id,
            "photo_message_id": photo_message_id,
            "details_message_id": details_message_id,
            "fallback_text": fallback_text,
            "photo_error": photo_error,
            "channel": channel,
            "commit_sha": os.getenv("VERCEL_GIT_COMMIT_SHA", ""),
        }
        if row is None:
            row = AppSetting(key=SETTING_KEY, value=new_state)
            session.add(row)
        else:
            row.value = new_state
        session.commit()
        LOGGER.info("Published Sector release %s to %s (fallback=%s)", release_id, channel, fallback_text)
        return {"ok": True, "published": True, "release_id": release_id, "channel": channel, "fallback_text": fallback_text}
    except Exception as exc:
        session.rollback()
        LOGGER.warning("Sector release publish failed: %s", exc)
        return {"ok": False, "published": False, "release_id": release_id, "error": str(exc)[:180]}
    finally:
        session.close()

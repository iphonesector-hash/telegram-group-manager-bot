import io
import json
import logging
import os
from pathlib import Path

from PIL import Image, ImageDraw

from bot.database.models import AppSetting
from bot.database.session import get_session

LOGGER = logging.getLogger(__name__)
BASE_DIR = Path(__file__).resolve().parents[2]
MANIFEST_PATH = BASE_DIR / "release" / "current.json"
DEFAULT_CHANNEL = os.getenv("SECTOR_RELEASE_CHANNEL", "@sectorlandS")
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


def _build_release_card(manifest):
    """Create a Telegram-safe PNG card without depending on CDN/static assets."""
    width, height = 1200, 675
    image = Image.new("RGB", (width, height), (8, 11, 31))
    draw = ImageDraw.Draw(image, "RGBA")

    # background glows
    draw.ellipse((-180, -240, 650, 590), fill=(92, 75, 255, 70))
    draw.ellipse((620, 120, 1430, 930), fill=(0, 214, 195, 42))
    draw.rounded_rectangle((54, 54, 1146, 621), radius=46, fill=(16, 21, 55, 235), outline=(120, 100, 255, 160), width=4)

    # mascot shell
    cx, cy = 880, 320
    draw.rounded_rectangle((720, 145, 1040, 475), radius=104, fill=(34, 40, 88, 255), outline=(124, 104, 255, 255), width=12)
    draw.rounded_rectangle((750, 182, 1010, 392), radius=72, fill=(8, 23, 48, 255), outline=(66, 220, 242, 255), width=8)
    draw.rounded_rectangle((790, 248, 842, 286), radius=16, fill=(103, 240, 255, 255))
    draw.rounded_rectangle((918, 248, 970, 286), radius=16, fill=(103, 240, 255, 255))
    draw.arc((835, 272, 925, 350), start=10, end=170, fill=(103, 240, 255, 255), width=10)
    draw.ellipse((842, 405, 918, 481), fill=(12, 27, 58, 255), outline=(103, 240, 255, 255), width=8)
    draw.polygon([(880, 420), (899, 443), (880, 468), (861, 443)], fill=(255, 199, 65, 255))

    # branding and release metadata. Keep text ASCII-safe for the default font.
    version = str(manifest.get("version") or "")[:20]
    release_id = str(manifest.get("release_id") or "")[-18:]
    draw.text((110, 120), "SECTOR", fill=(255, 255, 255, 255))
    draw.text((110, 175), "KOOCHOOLOO UPDATE", fill=(142, 226, 255, 255))
    draw.text((110, 245), f"VERSION {version}", fill=(255, 205, 76, 255))
    draw.text((110, 315), "PLAY  •  EARN  •  GROW", fill=(201, 198, 226, 255))
    draw.text((110, 390), "NEW FEATURES + GUIDES", fill=(201, 198, 226, 255))
    draw.text((110, 445), "@sectorlandS", fill=(142, 226, 255, 255))
    draw.text((110, 515), release_id, fill=(121, 128, 166, 255))

    output = io.BytesIO()
    output.name = "sector-release.png"
    image.save(output, format="PNG", optimize=True)
    output.seek(0)
    return output


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

    A generated PNG is uploaded directly to Telegram. If image generation or
    upload fails, the announcement still ships as text so no release is lost.
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
                photo=_build_release_card(manifest),
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

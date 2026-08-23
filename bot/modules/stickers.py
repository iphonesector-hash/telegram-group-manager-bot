import io
import os
from collections import deque
from pathlib import Path

from PIL import Image
from telegram import InputSticker, Update
from telegram.error import BadRequest
from telegram.ext import CommandHandler, ContextTypes

OWNER_ID = int(os.getenv("OWNER_ID", "5147526780"))
BASE_DIR = Path(__file__).resolve().parents[2]
SHEET_PATH = BASE_DIR / "public" / "assets" / "sector" / "mascot-emotions.webp"
EMOJIS = ["❤️", "⚡", "🏆", "🥹", "😢", "😡", "😴", "👑"]


def _remove_edge_background(image: Image.Image) -> Image.Image:
    image = image.convert("RGBA")
    px = image.load()
    width, height = image.size
    queue = deque()
    visited = set()

    def is_background(x, y):
        red, green, blue, alpha = px[x, y]
        return alpha > 0 and blue >= red + 16 and blue >= green + 5 and red < 90 and green < 105 and blue < 200

    for x in range(width):
        if is_background(x, 0): queue.append((x, 0))
        if is_background(x, height - 1): queue.append((x, height - 1))
    for y in range(height):
        if is_background(0, y): queue.append((0, y))
        if is_background(width - 1, y): queue.append((width - 1, y))

    while queue:
        x, y = queue.popleft()
        if (x, y) in visited or not is_background(x, y):
            continue
        visited.add((x, y))
        red, green, blue, _ = px[x, y]
        px[x, y] = (red, green, blue, 0)
        for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in visited:
                queue.append((nx, ny))
    return image


def _build_sticker_bytes():
    if not SHEET_PATH.exists():
        raise FileNotFoundError(str(SHEET_PATH))
    sheet = Image.open(SHEET_PATH).convert("RGBA")
    width, height = sheet.size
    top = max(34, int(height * 0.12))
    cell_width = width / 4
    cell_height = (height - top) / 2
    result = []

    for row in range(2):
        for column in range(4):
            x0 = int(round(column * cell_width))
            x1 = int(round((column + 1) * cell_width))
            y0 = int(round(top + row * cell_height))
            y1 = int(round(top + (row + 1) * cell_height))
            crop = _remove_edge_background(sheet.crop((x0, y0, x1, y1)))
            bbox = crop.getchannel("A").getbbox()
            if bbox:
                crop = crop.crop(bbox)
            scale = min(430 / max(1, crop.width), 430 / max(1, crop.height))
            crop = crop.resize((max(1, int(crop.width * scale)), max(1, int(crop.height * scale))), Image.Resampling.LANCZOS)
            canvas = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
            canvas.alpha_composite(crop, ((512 - crop.width) // 2, (512 - crop.height) // 2))
            buffer = io.BytesIO()
            canvas.save(buffer, format="PNG", optimize=True)
            payload = buffer.getvalue()
            if len(payload) > 512 * 1024:
                buffer = io.BytesIO()
                canvas.save(buffer, format="WEBP", lossless=True, method=6)
                payload = buffer.getvalue()
            result.append(payload)
    return result


async def sector_stickers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    message = update.effective_message
    if not user or not message or int(user.id) != OWNER_ID:
        return

    me = await context.bot.get_me()
    username = (me.username or "iSectorlandbot").lower()
    set_name = f"sector_koochooloo_by_{username}"
    set_url = f"https://t.me/addstickers/{set_name}"

    try:
        await context.bot.get_sticker_set(set_name)
        await message.reply_text("✅ پک استیکر Sector Koochooloo قبلاً ساخته شده:\n" + set_url)
        return
    except BadRequest:
        pass

    await message.reply_text("🎨 در حال ساخت پک استیکر Sector Koochooloo...")
    try:
        payloads = _build_sticker_bytes()
        stickers = [InputSticker(sticker=payload, emoji_list=[EMOJIS[index]], format="static") for index, payload in enumerate(payloads)]
        await context.bot.create_new_sticker_set(
            user_id=user.id,
            name=set_name,
            title="Sector Koochooloo • سکتور کوچولو",
            stickers=stickers,
        )
        await message.reply_text("✅ پک استیکر رسمی سکتور کوچولو ساخته شد:\n" + set_url)
    except Exception as exc:
        await message.reply_text("❌ ساخت پک استیکر انجام نشد: " + str(exc)[:180])


def get_handlers():
    return [CommandHandler("sectorstickers", sector_stickers)]

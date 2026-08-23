import io
import math
import os

from PIL import Image, ImageDraw
from telegram import InputSticker, Update
from telegram.error import BadRequest
from telegram.ext import CommandHandler, ContextTypes

OWNER_ID = int(os.getenv("OWNER_ID", "5147526780"))
EMOJIS = ["❤️", "⚡", "🏆", "🥹", "😢", "😡", "😴", "👑"]


def _draw_sector_mascot(index: int) -> bytes:
    """Generate one transparent 512x512 Sector mascot sticker.

    Kept procedural on purpose so sticker generation never depends on a web
    asset, CDN, font, or browser decoder inside a Vercel serverless runtime.
    """
    canvas = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)

    # soft glow layers
    for radius, alpha in ((190, 24), (165, 34), (140, 46)):
        box = (256 - radius, 260 - radius, 256 + radius, 260 + radius)
        draw.ellipse(box, fill=(105, 86, 255, alpha))

    # ears / antenna shapes
    draw.rounded_rectangle((92, 128, 176, 244), radius=34, fill=(55, 62, 115, 255), outline=(132, 113, 255, 255), width=8)
    draw.rounded_rectangle((336, 128, 420, 244), radius=34, fill=(55, 62, 115, 255), outline=(132, 113, 255, 255), width=8)

    # head shell
    draw.rounded_rectangle((120, 118, 392, 394), radius=92, fill=(26, 31, 72, 255), outline=(119, 102, 255, 255), width=12)
    draw.rounded_rectangle((146, 154, 366, 328), radius=66, fill=(9, 18, 42, 255), outline=(42, 205, 236, 255), width=8)

    # visor glow
    draw.rounded_rectangle((162, 172, 350, 306), radius=56, fill=(13, 39, 67, 255))

    eye_y = 220
    eye_color = (93, 240, 255, 255)
    accent = (255, 202, 71, 255)

    if index == 3:  # teary/cute
        draw.ellipse((192, eye_y - 12, 222, eye_y + 18), fill=eye_color)
        draw.ellipse((290, eye_y - 12, 320, eye_y + 18), fill=eye_color)
        draw.ellipse((203, 252, 216, 276), fill=(99, 184, 255, 220))
        draw.arc((226, 244, 286, 290), start=205, end=335, fill=eye_color, width=7)
    elif index == 4:  # sad
        draw.arc((184, 204, 230, 246), start=210, end=330, fill=eye_color, width=9)
        draw.arc((282, 204, 328, 246), start=210, end=330, fill=eye_color, width=9)
        draw.arc((224, 258, 288, 304), start=200, end=340, fill=eye_color, width=8)
        draw.ellipse((304, 246, 319, 274), fill=(99, 184, 255, 225))
    elif index == 5:  # angry
        draw.line((185, 206, 229, 224), fill=eye_color, width=10)
        draw.line((327, 206, 283, 224), fill=eye_color, width=10)
        draw.line((232, 279, 280, 279), fill=eye_color, width=8)
    elif index == 6:  # sleepy
        draw.arc((180, 206, 234, 246), start=10, end=170, fill=eye_color, width=8)
        draw.arc((278, 206, 332, 246), start=10, end=170, fill=eye_color, width=8)
        draw.ellipse((248, 266, 270, 286), outline=eye_color, width=6)
        draw.text((360, 98), "Z", fill=(198, 193, 255, 255))
        draw.text((394, 70), "Z", fill=(198, 193, 255, 220))
    else:
        draw.rounded_rectangle((188, 210, 226, 240), radius=14, fill=eye_color)
        draw.rounded_rectangle((286, 210, 324, 240), radius=14, fill=eye_color)
        if index in (0, 1, 2, 7):
            draw.arc((225, 236, 287, 286), start=15, end=165, fill=eye_color, width=8)
        else:
            draw.line((238, 270, 274, 270), fill=eye_color, width=7)

    # chest/core
    draw.ellipse((222, 336, 290, 404), fill=(14, 25, 56, 255), outline=(93, 240, 255, 255), width=7)
    draw.polygon([(256, 348), (271, 371), (256, 394), (241, 371)], fill=accent)

    # theme decoration per sticker
    if index == 0:  # love
        heart = [(82, 86), (64, 62), (30, 70), (26, 103), (82, 156), (138, 103), (134, 70), (100, 62)]
        draw.polygon(heart, fill=(255, 91, 137, 245))
    elif index == 1:  # energy
        draw.polygon([(407, 70), (360, 155), (398, 155), (368, 230), (454, 128), (412, 128)], fill=(255, 215, 75, 250))
    elif index == 2:  # trophy
        draw.rounded_rectangle((376, 62, 454, 132), radius=16, fill=(255, 196, 56, 250))
        draw.rectangle((405, 126, 425, 162), fill=(255, 196, 56, 250))
        draw.rounded_rectangle((390, 158, 440, 178), radius=9, fill=(255, 196, 56, 250))
    elif index == 7:  # crown
        crown = [(178, 102), (198, 60), (228, 94), (256, 50), (284, 94), (314, 60), (334, 102), (324, 126), (188, 126)]
        draw.polygon(crown, fill=(255, 201, 64, 250), outline=(255, 235, 153, 255))

    # tiny stars for celebratory variants
    if index in (0, 1, 2, 7):
        for angle in (0.4, 2.1, 4.4):
            cx = int(256 + math.cos(angle) * 206)
            cy = int(260 + math.sin(angle) * 185)
            draw.ellipse((cx - 7, cy - 7, cx + 7, cy + 7), fill=(188, 181, 255, 230))

    buffer = io.BytesIO()
    canvas.save(buffer, format="PNG", optimize=True)
    return buffer.getvalue()


def _build_sticker_bytes():
    return [_draw_sector_mascot(index) for index in range(len(EMOJIS))]


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

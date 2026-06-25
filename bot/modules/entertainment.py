import random
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

JOKES = [
    "‏يه بار يه پسره ميخواست بره خواستگاری، باباش ميگه برو يه گل بگير. ميگه بابا گل كه دارم، ميگه نه احمق برو گلفروشی! 😂",
    "‏طرف ميره دكتر، دكتر ميگه چرا اينجوری شدی؟ ميگه آقای دكتر من هر شب خواب ميبينم با پنگوئن‌ها فوتبال بازی ميكنم. دكتر ميگه برو اين قرص‌ها رو بخور، از فردا شب ديگه خواب پنگوئن نميبينی. ميگه آقای دكتر ميشه از پس‌فردا شب بخورم؟ آخه امشب فيناله! 🐧⚽️",
    "‏ميدونيد چرا غواص‌ها از پشت ميوفتن تو آب؟ چون اگه از جلو بيافتن ميوفتن تو قايق! 😂",
]

FACTS = [
    "آیا می‌دانستید که هشت‌پاها سه قلب دارند؟ 🐙",
    "آیا می‌دانستید که عسل تنها ماده غذایی است که هرگز فاسد نمی‌شود؟ 🍯",
    "آیا می‌دانستید که مورچه‌ها هرگز نمی‌خوابند؟ 🐜",
]

RIDDLES = [
    {"q": "آن چیست که چشم دارد اما نمی‌بیند؟", "a": "سوزن 🪡"},
    {"q": "آن چیست که پا دارد اما راه نمی‌رود؟", "a": "میز 🪑"},
    {"q": "آن چیست که مال شماست اما دیگران بیشتر از آن استفاده می‌کنند؟", "a": "اسم شما 👤"},
]

STORIES = [
    "روزی روزگاری در روستایی دورافتاده، مردی زندگی می‌کرد که معتقد بود می‌تواند با پرندگان صحبت کند...",
    "در زمان‌های قدیم، پادشاهی عادل بود که برای فهمیدن مشکلات مردم، شب‌ها با لباس مبدل در شهر قدم می‌زد...",
]

CHALLENGES = [
    "همین الان ۳ بار بلند بگو: «چای داغ، دایی چاق»! 🍵",
    "بدون اینکه پلک بزنی ۳۰ ثانیه به صفحه گوشی نگاه کن! 👀",
    "نام ۵ شهر ایران که با حرف «س» شروع می‌شوند را بگو. 🗺",
]

async def joke_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(random.choice(JOKES))

async def fact_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"💡 {random.choice(FACTS)}")

async def riddle_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    riddle = random.choice(RIDDLES)
    await update.message.reply_text(f"❓ {riddle['q']}\n\n.\n.\n.\n✅ پاسخ: {riddle['a']}")

async def story_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"📖 {random.choice(STORIES)}")

async def dice_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_dice()

async def coin_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    res = random.choice(["شیر 🦁", "خط 📏"])
    await update.message.reply_text(f"🪙 سکه انداخته شد:\n\nنتیجه: **{res}**", parse_mode="Markdown")

async def challenge_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"🎯 چالش:\n\n{random.choice(CHALLENGES)}")

def get_handlers():
    return [
        CommandHandler("joke", joke_cmd),
        CommandHandler("fact", fact_cmd),
        CommandHandler("riddle", riddle_cmd),
        CommandHandler("story", story_cmd),
        CommandHandler("dice", dice_cmd),
        CommandHandler("coin", coin_cmd),
        CommandHandler("challenge", challenge_cmd),
    ]

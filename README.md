# 🌐 iSectorLand Unified Bot + Mini App

این ریپو از این به بعد **تنها منبع اصلی (canonical)** برای ربات `@iSectorlandbot`، مدیریت گروه و Telegram Mini App است.

## منابعی که در این پروژه ادغام شده‌اند

- `iphonesector-hash/telegram-group-manager-bot` — هسته اصلی و Mini App React/Vite
- `iphonesector-hash/iSectorLandBot` — قابلیت‌های قدیمی مدیریت، بانک، سرگرمی و ابزارها
- `iphonesector-hash/Mini-app-sector` — طراحی و ایده‌های Mini App قدیمی

ریپوهای دوم و سوم فقط به‌عنوان Legacy Reference باقی می‌مانند و نباید Deployment جداگانه داشته باشند.

## قابلیت‌های هسته

- مدیریت گروه، قفل‌ها، خوش‌آمدگویی و قوانین
- اخطار، میوت، بن/کیک و Anti-Spam
- پروفایل، XP، Level و Leaderboard
- SectorBank: کیف پول، بانک، انتقال، وام و جایزه روزانه
- سرگرمی، بازی‌ها، فال/معما/دانستنی
- دستیار AI فارسی با قابلیت جستجو
- Telegram Mini App با پروفایل، فروشگاه، کیف پول، بازی‌ها، سفارش‌ها، دعوت و پشتیبانی
- FastAPI برای Mini App
- Telegram Webhook مناسب Vercel Serverless
- PostgreSQL/Supabase برای داده‌های پایدار

## Runtime Production

Vercel نباید `app.run_polling()` را اجرا کند. Production از Telegram Webhook استفاده می‌کند:

`POST /api/telegram`

اجرای polling فقط برای توسعه محلی است:

```bash
python -m bot.main
```

## Environment Variables

فایل `.env.example` را ببینید. موارد ضروری Production:

- `BOT_TOKEN`
- `TELEGRAM_WEBHOOK_SECRET`
- `DATABASE_URL`
- `VITE_API_BASE_URL`

AI اختیاری است و از `GROQ_API_KEY` و در صورت نیاز `TAVILY_API_KEY` استفاده می‌کند.

## Security

توکن Telegram نباید داخل سورس یا Git history جدید قرار بگیرد. Tokenهای قدیمی که قبلاً در ریپو یا چت قرار گرفته‌اند باید بعد از Cut-over نهایی Rotate شوند.

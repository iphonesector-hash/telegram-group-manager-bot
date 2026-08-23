# Sector v2 Production Graphics Engine

Sector v2 uses a lightweight vector-first graphics engine in production. The separately generated PNG/GIF/WebM art pack remains the visual master/reference pack, while the Mini App renders equivalent stage, mood, wearable, care, reward and event visuals directly with React/SVG.

## Why vector-first in production

- No external asset host or network dependency for core Sector visuals.
- Immediate live preview of equipped and not-yet-purchased wearables.
- Small payload and lower memory pressure inside Telegram WebView on iPhone.
- Crisp rendering across screen densities.
- Animations respect the existing Mini App motion/performance model and degrade safely if CSS animation is reduced.

## Coverage

- Six evolution stages: Scrap, Patched, Core, Advanced, Elite, Mythic.
- Mood-aware eyes and body treatment.
- Layered slots: background, aura, back, body, face, head and hand.
- Shop thumbnails derived from slot/rarity/item identity.
- Animated care art for charge, play, train, learn, repair, feed, clean and sleep.
- Reward, mission, level, Bond, victory and World Boss stickers.

## Raster master pack

The production design pack was also generated as standalone PNG, GIF and WebM assets and is kept as the master art package for future Telegram stickers, marketing, richer cinematic moments and optional replacement layers. Core gameplay does not break if those raster files are unavailable.

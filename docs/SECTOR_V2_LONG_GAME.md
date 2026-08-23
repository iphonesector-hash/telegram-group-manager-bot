# Sector Companion v2.1 — Long Game

## Systems
- Monthly Season Points + leaderboard + previous-season rewards.
- World Boss with shared HP, 30-minute per-user cooldown, energy cost and row locking.
- Bond derived from visit/gift/battle interactions.
- Daily/weekly missions and lifetime quests with unique claim constraints.
- Permanent evolution path selection and level-based unlocks.
- Store preview, equip/unequip and 50% resale from level 5.
- Sector-specific ledger and lightweight analytics.
- Memory compaction after large history growth.
- Server-side Telegram initData + required-channel membership guard on Sector v2/meta APIs.

## Abuse controls
- Existing care cooldown and daily reward caps remain active.
- Social rewards remain once per action/target/day.
- Minigame paid rewards remain capped per day.
- Boss attacks cost energy and are limited by cooldown.
- Reward claims are protected by database uniqueness and IntegrityError handling.
- Boss HP mutation is serialized with SELECT FOR UPDATE in the attack route.

## Pre-deploy rule
The release candidate stays unattached to `main` until static QA, database integrity checks and route/API audits pass. Real Telegram WebView/initData interaction is tested only after the single final production deploy.

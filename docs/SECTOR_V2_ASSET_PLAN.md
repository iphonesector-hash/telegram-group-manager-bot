# Sector Companion v2 — Visual Asset Contract

The Mini App now has a vector fallback renderer, so missing media must never produce a blank companion. Final media can progressively replace vector layers without changing economy or inventory data.

## Character evolution masters

Create six transparent character masters using the same pose, camera, body proportions and anchor points:

1. `scrap` — dented shell, loose antenna, exposed cable, rust, mismatched plates.
2. `patched` — repaired plates, tape/bolts, cleaner visor, still visibly old.
3. `core` — stable chassis, clean face panel, modern sensor light.
4. `advanced` — redesigned armor, better joints and display.
5. `elite` — premium materials and compact high-tech silhouette.
6. `mythic` — final form; elegant, powerful and rare without childish styling.

Required states per stage: idle, happy, tired, hungry, dirty, sleep, repair, feed, clean, level-up. Static fallback: PNG/WebP. Motion: WebM with alpha where possible, GIF only as a Telegram-compatible fallback.

## Wearable slots

All wearable exports use the exact same 1024x1024 transparent canvas as the character master. Never crop to the visible object.

- head: 8–12 items
- face: 6–10 items
- body: 10–16 items
- back: 8–12 items
- hand: 8–12 items
- aura: 6–10 looping effects
- background: 8–12 scenes

Initial item IDs are defined in `bot/services/sector_v2.py`. Asset filenames should match IDs, e.g. `commander_cap.webp` and `commander_cap.webm`.

## Animation events

Priority motion pack: `care_feed`, `care_clean`, `care_sleep`, `care_repair`, `coin_gain`, `purchase_success`, `equip_item`, `level_up`, `stage_evolution`, `duel_win`, `duel_loss`, `gift_send`, `memory_saved`.

## Telegram animated emoji intake

Owner-supplied Premium custom emoji IDs are kept separate from web assets. They may be used for Telegram messages and buttons, while the Mini App uses transparent WebM/PNG equivalents. Never depend on Premium emoji availability for core UI.

## Art direction

Industrial sci-fi, compact robot, slightly worn metal, dark neutral environment, restrained cyan/amber/violet accents. Avoid nursery/cartoon proportions, oversized emoji faces, toy-plastic materials and saturated rainbow UI. Sector should look collectible, not childish.

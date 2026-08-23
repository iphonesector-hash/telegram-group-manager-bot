# Sector v2 pre-deploy QA

This snapshot is intentionally kept off `main` until the final deploy decision.

Required checks before moving `main`:

- Python modules parse/import without syntax errors.
- Mini App Sector page and avatar JSX parse successfully.
- Every frontend Sector v2 API method maps to a registered backend route.
- Care actions include charge/play/train/learn/repair/feed/clean/sleep.
- PostgreSQL action constraint accepts feed/clean/sleep/story as well as legacy actions.
- Existing inventory keys remain recognized and equipped appearance is preserved.
- Shop preview never deducts coins; purchase/equip are separate server actions.
- Sector chat works inside Mini App and falls back locally when AI/history persistence fails.
- Memories are read from SectorPetMemory and chat/care/shop events can add memories.
- Sector v2 API is protected by Telegram initData and required-channel membership server-side.
- Group bottom keyboard remains usable; group navigation does not redirect to private chat.
- Group navigation/actions edit one persistent topic panel wherever possible.
- Inline button semantics: primary=blue navigation/info, success=green positive/reward, danger=red sensitive/competitive.
- Social Reply panel retains battle/gift/visit/profile actions and does not create a new message for each callback.
- No `main` ref update or Vercel deployment occurs until all above checks pass.

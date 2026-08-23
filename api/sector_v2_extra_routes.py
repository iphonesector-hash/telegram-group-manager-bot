from typing import Optional

from fastapi import Header

from api.main import app, require_user
from api.sector_v2_routes import _require_member
from bot.database.models import SectorPet, User
from bot.database.session import get_session
from bot.services import sector_pet as legacy


@app.get("/api/sector-v2-leaderboard")
async def sector_v2_guarded_leaderboard(init_data: Optional[str] = Header(None, alias="init-data")):
    telegram_user = require_user(init_data)
    await _require_member(int(telegram_user["id"]))
    session = get_session()
    try:
        rows = (
            session.query(SectorPet, User)
            .join(User, User.id == SectorPet.user_id)
            .order_by(SectorPet.xp.desc())
            .limit(30)
            .all()
        )
        return [
            {
                "rank": i + 1,
                "name": pet.name,
                "owner": user.first_name,
                "level": legacy.level_from_xp(pet.xp),
                "xp": int(pet.xp or 0),
                "path": pet.evolution_path,
            }
            for i, (pet, user) in enumerate(rows)
        ]
    finally:
        session.close()

"""API package bootstrap for Vercel.

Importing these modules registers Sector routes on the shared FastAPI app
before api.index finishes loading.
"""
import os

# Some hosting environments can define OWNER_ID as an empty string. Normalize
# it before api.index or any bot module evaluates integer owner settings.
if not (os.getenv("OWNER_ID") or "").strip():
    os.environ["OWNER_ID"] = "5147526780"

from bot.services import sector_locale  # noqa: F401,E402
from api import sector_v2_routes  # noqa: F401,E402
from api import sector_v2_extra_routes  # noqa: F401,E402
from api import sector_meta_routes  # noqa: F401,E402
from bot.services import sector_mission_personalization  # noqa: F401,E402
from bot.services import sector_relationship_memory  # noqa: F401,E402
from bot.services import sector_coherence  # noqa: F401,E402
from api import sector_reminder_routes  # noqa: F401,E402
from api import sector_action_intent_routes  # noqa: F401,E402
from api import sector_diagnostics_routes  # noqa: F401,E402

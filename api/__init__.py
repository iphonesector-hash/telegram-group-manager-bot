"""API package bootstrap for Vercel.

Importing these modules registers Sector routes on the shared FastAPI app
before api.index finishes loading.
"""
from bot.services import sector_locale  # noqa: F401,E402
from api import sector_v2_routes  # noqa: F401,E402
from api import sector_v2_extra_routes  # noqa: F401,E402
from api import sector_meta_routes  # noqa: F401,E402
from bot.services import sector_mission_personalization  # noqa: F401,E402
from api import sector_reminder_routes  # noqa: F401,E402
from api import sector_action_intent_routes  # noqa: F401,E402

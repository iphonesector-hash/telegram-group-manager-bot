from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL, make_url
from sqlalchemy.orm import sessionmaker
from bot.database.models import Base
import os

DATABASE_URL = os.getenv("DATABASE_URL")
engine = None
SessionLocal = None

PROJECT_REF = "yqefvpuegmpibyupnsjj"
PROJECT_REGION = "eu-west-1"
# This project is on the aws-1 pooler cluster. Older Vercel env values pointed
# to aws-0, which returns tenant/user not found for this project.
PROJECT_POOLER_CLUSTER = "1"


def _pooler_url(url, project_ref: str) -> str:
    pooled = URL.create(
        drivername="postgresql+psycopg2",
        username=f"postgres.{project_ref}",
        password=url.password,
        host=f"aws-{PROJECT_POOLER_CLUSTER}-{PROJECT_REGION}.pooler.supabase.com",
        port=6543,
        database=url.database or "postgres",
    )
    return pooled.render_as_string(hide_password=False)


def _normalize_database_url(raw_url: str) -> str:
    if raw_url.startswith("postgres://"):
        raw_url = raw_url.replace("postgres://", "postgresql://", 1)

    url = make_url(raw_url)
    host = (url.host or "").lower()

    # Direct Supabase DB URL -> transaction pooler for reliable Vercel egress.
    if host.startswith("db.") and host.endswith(".supabase.co"):
        parts = host.split(".")
        project_ref = parts[1] if len(parts) >= 4 else PROJECT_REF
        return _pooler_url(url, project_ref)

    # Repair stale/incorrect Supabase pooler hosts (notably aws-0 from the old
    # Vercel configuration) while preserving the existing database password.
    if host.endswith(".pooler.supabase.com"):
        username = url.username or ""
        project_ref = PROJECT_REF
        if username.startswith("postgres.") and len(username.split(".", 1)) == 2:
            project_ref = username.split(".", 1)[1] or PROJECT_REF
        expected_host = f"aws-{PROJECT_POOLER_CLUSTER}-{PROJECT_REGION}.pooler.supabase.com"
        expected_user = f"postgres.{project_ref}"
        if host != expected_host or username != expected_user or url.port != 6543:
            return _pooler_url(url, project_ref)

    return raw_url


if DATABASE_URL:
    DATABASE_URL = _normalize_database_url(DATABASE_URL)
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300,
        pool_timeout=10,
        connect_args={"connect_timeout": 10, "sslmode": "require"},
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def _require_database():
    if engine is None or SessionLocal is None:
        raise RuntimeError("DATABASE_URL is required for database-backed bot features.")


def init_db():
    _require_database()
    Base.metadata.create_all(engine)
    # create_all does not add columns to an existing table. Keep this migration
    # additive and idempotent so old Sector companions remain intact.
    if engine.url.get_backend_name() == "postgresql":
        statements = (
            "ALTER TABLE isectorbot_sector_pets ADD COLUMN IF NOT EXISTS hunger INTEGER NOT NULL DEFAULT 80",
            "ALTER TABLE isectorbot_sector_pets ADD COLUMN IF NOT EXISTS cleanliness INTEGER NOT NULL DEFAULT 80",
            "ALTER TABLE isectorbot_sector_pets ADD COLUMN IF NOT EXISTS personality TEXT NOT NULL DEFAULT 'کنجکاو'",
            "ALTER TABLE isectorbot_sector_pets ADD COLUMN IF NOT EXISTS room_level INTEGER NOT NULL DEFAULT 1",
            "ALTER TABLE isectorbot_sector_pets ADD COLUMN IF NOT EXISTS inventory JSON NOT NULL DEFAULT '{}'::json",
            "ALTER TABLE isectorbot_sector_pets ADD COLUMN IF NOT EXISTS equipped_item TEXT",
            "ALTER TABLE isectorbot_sector_pets ADD COLUMN IF NOT EXISTS sleeping BOOLEAN NOT NULL DEFAULT FALSE",
        )
        with engine.begin() as connection:
            for statement in statements:
                connection.execute(text(statement))
    print(f"✅ iSectorLand database ready ({engine.url.get_backend_name()}).")


def get_session():
    _require_database()
    return SessionLocal()

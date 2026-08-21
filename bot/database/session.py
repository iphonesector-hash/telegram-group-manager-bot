from sqlalchemy import create_engine
from sqlalchemy.engine import URL, make_url
from sqlalchemy.orm import sessionmaker
from bot.database.models import Base
import os

DATABASE_URL = os.getenv("DATABASE_URL")
engine = None
SessionLocal = None


def _normalize_database_url(raw_url: str) -> str:
    if raw_url.startswith("postgres://"):
        raw_url = raw_url.replace("postgres://", "postgresql://", 1)

    url = make_url(raw_url)
    host = url.host or ""

    # Supabase Direct connections are IPv6-first. Vercel serverless may not have
    # usable IPv6 egress, so transparently route Direct URLs through Supabase's
    # transaction pooler while preserving the configured database password.
    if host.startswith("db.") and host.endswith(".supabase.co"):
        parts = host.split(".")
        if len(parts) >= 4:
            project_ref = parts[1]
            region = os.getenv("SUPABASE_DB_REGION", "eu-west-1")
            pooled = URL.create(
                drivername="postgresql+psycopg2",
                username=f"postgres.{project_ref}",
                password=url.password,
                host=f"aws-0-{region}.pooler.supabase.com",
                port=6543,
                database=url.database or "postgres",
            )
            return pooled.render_as_string(hide_password=False)

    return raw_url


if DATABASE_URL:
    DATABASE_URL = _normalize_database_url(DATABASE_URL)
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300,
        pool_timeout=10,
        connect_args={"connect_timeout": 10},
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def _require_database():
    if engine is None or SessionLocal is None:
        raise RuntimeError("DATABASE_URL is required for database-backed bot features.")


def init_db():
    _require_database()
    Base.metadata.create_all(engine)
    print(f"✅ iSectorLand database ready ({engine.url.get_backend_name()}).")


def get_session():
    _require_database()
    return SessionLocal()

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from bot.database.models import Base
import os

DATABASE_URL = os.getenv("DATABASE_URL")
engine = None
SessionLocal = None

if DATABASE_URL:
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300,
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

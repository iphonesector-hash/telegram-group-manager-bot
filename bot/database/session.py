from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from bot.database.models import Base
import os

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is required; local SQLite fallback is disabled in production.")

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    # Tables are managed by Supabase migrations. create_all is idempotent and useful
    # for local/dev parity, but all runtime models are namespaced with isectorbot_.
    Base.metadata.create_all(engine)
    print(f"✅ iSectorLand database ready ({engine.url.get_backend_name()}).")


def get_session():
    return SessionLocal()

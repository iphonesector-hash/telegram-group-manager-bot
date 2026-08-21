from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker
from bot.database.models import Base
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///bot_database.db")

# Supabase/Heroku-style URLs sometimes use postgres://, while SQLAlchemy 2 expects postgresql://.
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine_kwargs = {"pool_pre_ping": True}
if DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    engine_kwargs.update({"pool_recycle": 300})

engine = create_engine(DATABASE_URL, **engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def _add_missing_columns(conn, inspector, table_name: str, columns: dict[str, str]):
    existing = {c["name"] for c in inspector.get_columns(table_name)}
    for col, col_type in columns.items():
        if col not in existing:
            conn.execute(text(f'ALTER TABLE "{table_name}" ADD COLUMN "{col}" {col_type}'))


def init_db():
    Base.metadata.create_all(engine)
    inspector = inspect(engine)
    with engine.begin() as conn:
        if inspector.has_table("groups"):
            _add_missing_columns(conn, inspector, "groups", {
                "prevent_bots": "BOOLEAN DEFAULT FALSE",
                "new_member_limit": "BOOLEAN DEFAULT FALSE",
                "approval_mode": "BOOLEAN DEFAULT FALSE",
                "activity_logging": "BOOLEAN DEFAULT TRUE",
                "rules_enabled": "BOOLEAN DEFAULT TRUE",
            })
        if inspector.has_table("users"):
            _add_missing_columns(conn, inspector, "users", {
                "bank_balance": "BIGINT DEFAULT 0",
                "loan_balance": "BIGINT DEFAULT 0",
                "vip_until": "TIMESTAMP NULL",
            })

    print(f"✅ Database initialized ({engine.url.get_backend_name()}).")


def get_session():
    return SessionLocal()

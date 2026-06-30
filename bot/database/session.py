from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker
from bot.database.models import Base
import os

DATABASE_URL = "sqlite:///bot_database.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(engine)
    inspector = inspect(engine)
    with engine.connect() as conn:
        # Groups migration
        group_cols = [c['name'] for c in inspector.get_columns('groups')]
        for col, ctype in {'prevent_bots':'BOOLEAN DEFAULT 0','new_member_limit':'BOOLEAN DEFAULT 0','approval_mode':'BOOLEAN DEFAULT 0','activity_logging':'BOOLEAN DEFAULT 1','rules_enabled':'BOOLEAN DEFAULT 1'}.items():
            if col not in group_cols:
                try: conn.execute(text(f"ALTER TABLE groups ADD COLUMN {col} {ctype}"))
                except: pass
        # Users migration
        user_cols = [c['name'] for c in inspector.get_columns('users')]
        if "last_wheel_spin" not in user_cols:
            try: conn.execute(text("ALTER TABLE users ADD COLUMN last_wheel_spin DATETIME"))
            except: pass
        conn.commit()

def get_session():
    return SessionLocal()

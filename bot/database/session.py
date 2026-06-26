from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker
from bot.database.models import Base
import os

DATABASE_URL = "sqlite:///bot_database.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    # Create tables if they don't exist
    Base.metadata.create_all(engine)

    # Auto-migration: Check for missing columns
    inspector = inspect(engine)
    with engine.connect() as conn:
        # Check users table
        columns = [c['name'] for c in inspector.get_columns('users')]
        if 'last_daily_claim' not in columns:
            conn.execute(text("ALTER TABLE users ADD COLUMN last_daily_claim DATETIME"))

        # Check groups table
        columns = [c['name'] for c in inspector.get_columns('groups')]
        if 'ai_enabled' not in columns:
            conn.execute(text("ALTER TABLE groups ADD COLUMN ai_enabled BOOLEAN DEFAULT 1"))
        if 'economy_enabled' not in columns:
            conn.execute(text("ALTER TABLE groups ADD COLUMN economy_enabled BOOLEAN DEFAULT 1"))

        # Add more migration checks as needed
        conn.commit()

    print("✅ Database initialized and migrated successfully.")

def get_session():
    return SessionLocal()

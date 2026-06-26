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
    Base.metadata.create_all(engine)

    inspector = inspect(engine)
    with engine.connect() as conn:
        columns = [c['name'] for c in inspector.get_columns('groups')]

        new_columns = {
            'prevent_bots': 'BOOLEAN DEFAULT 0',
            'new_member_limit': 'BOOLEAN DEFAULT 0',
            'approval_mode': 'BOOLEAN DEFAULT 0',
            'activity_logging': 'BOOLEAN DEFAULT 1'
        }

        for col, col_type in new_columns.items():
            if col not in columns:
                conn.execute(text(f"ALTER TABLE groups ADD COLUMN {col} {col_type}"))

        conn.commit()

    print("✅ Database initialized and migrated successfully.")

def get_session():
    return SessionLocal()

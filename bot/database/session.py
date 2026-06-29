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
        # Migrate groups table
        group_columns = [c['name'] for c in inspector.get_columns('groups')]
        new_group_columns = {
            'prevent_bots': 'BOOLEAN DEFAULT 0',
            'new_member_limit': 'BOOLEAN DEFAULT 0',
            'approval_mode': 'BOOLEAN DEFAULT 0',
            'activity_logging': 'BOOLEAN DEFAULT 1',
            'rules_enabled': 'BOOLEAN DEFAULT 1'
        }
        for col, col_type in new_group_columns.items():
            if col not in group_columns:
                try:
                    conn.execute(text(f"ALTER TABLE groups ADD COLUMN {col} {col_type}"))
                except:
                    pass

        # Migrate users table
        user_columns = [c['name'] for c in inspector.get_columns('users')]
        new_user_columns = {
            'last_wheel_spin': 'DATETIME'
        }
        for col, col_type in new_user_columns.items():
            if col not in user_columns:
                try:
                    conn.execute(text(f"ALTER TABLE users ADD COLUMN {col} {col_type}"))
                except:
                    pass

        conn.commit()

    print("✅ Database initialized and migrated successfully.")

def get_session():
    return SessionLocal()

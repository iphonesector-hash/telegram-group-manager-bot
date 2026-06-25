from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from bot.database.models import Base
import os

DATABASE_URL = "sqlite:///bot_database.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} # Needed for SQLite with multi-threading
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(engine)
    print("✅ Database initialized successfully.")

def get_session():
    return SessionLocal()

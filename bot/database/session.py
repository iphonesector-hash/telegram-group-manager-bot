from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from bot.database.models import Base
import os

DATABASE_URL = "sqlite:///bot_database.db"

engine = create_engine(DATABASE_URL)
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)

def init_db():
    Base.metadata.create_all(engine)
    print("✅ Database initialized successfully.")

def get_session():
    return Session()

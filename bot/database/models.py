from sqlalchemy import Column, Integer, BigInteger, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True)  # Telegram User ID
    username = Column(String, nullable=True)
    first_name = Column(String)

    coins = Column(BigInteger, default=0)
    xp = Column(BigInteger, default=0)
    level = Column(Integer, default=1)
    message_count = Column(BigInteger, default=0)

    last_daily_claim = Column(DateTime, nullable=True)

    # Bank Features
    loan_amount = Column(BigInteger, default=0)
    loan_due_date = Column(DateTime, nullable=True)

    is_admin = Column(Boolean, default=False)
    joined_at = Column(DateTime, default=datetime.datetime.utcnow)

class Group(Base):
    __tablename__ = "groups"

    id = Column(BigInteger, primary_key=True)  # Telegram Chat ID
    title = Column(String)

    # Locks
    lock_links = Column(Boolean, default=False)
    lock_usernames = Column(Boolean, default=False)
    lock_forward = Column(Boolean, default=False)
    lock_photos = Column(Boolean, default=False)
    lock_videos = Column(Boolean, default=False)
    lock_files = Column(Boolean, default=False)
    lock_stickers = Column(Boolean, default=False)
    lock_gifs = Column(Boolean, default=False)
    lock_voice = Column(Boolean, default=False)
    lock_contacts = Column(Boolean, default=False)

    # Welcome
    welcome_enabled = Column(Boolean, default=True)
    welcome_text = Column(Text, default="خوش اومدی به گروه 🌟\nلطفاً قوانین رو رعایت کن.")

    # Rules
    rules = Column(Text, nullable=True)

    # Anti-spam
    antispam_enabled = Column(Boolean, default=True)
    antispam_limit = Column(Integer, default=5) # messages per 10s

    # Economy
    economy_enabled = Column(Boolean, default=True)

    is_active = Column(Boolean, default=True)
    joined_at = Column(DateTime, default=datetime.datetime.utcnow)

class Warning(Base):
    __tablename__ = "warnings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"))
    group_id = Column(BigInteger, ForeignKey("groups.id"))
    reason = Column(String, default="بدون دلیل")
    warned_by = Column(BigInteger)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Mute(Base):
    __tablename__ = "mutes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"))
    group_id = Column(BigInteger, ForeignKey("groups.id"))
    until = Column(DateTime)  # When the mute expires
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

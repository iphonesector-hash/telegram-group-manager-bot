from sqlalchemy import Column, Integer, BigInteger, String, Boolean, DateTime, ForeignKey
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

    is_admin = Column(Boolean, default=False)
    joined_at = Column(DateTime, default=datetime.datetime.utcnow)

class Group(Base):
    __tablename__ = "groups"

    id = Column(BigInteger, primary_key=True)  # Telegram Chat ID
    title = Column(String)

    lock_links = Column(Boolean, default=False)
    lock_photos = Column(Boolean, default=False)
    lock_videos = Column(Boolean, default=False)
    lock_stickers = Column(Boolean, default=False)
    lock_forward = Column(Boolean, default=False)

    is_active = Column(Boolean, default=True)
    joined_at = Column(DateTime, default=datetime.datetime.utcnow)

class Warning(Base):
    __tablename__ = "warnings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"))
    group_id = Column(BigInteger, ForeignKey("groups.id"))
    reason = Column(String, default="No reason provided")
    warned_by = Column(BigInteger)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Mute(Base):
    __tablename__ = "mutes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"))
    group_id = Column(BigInteger, ForeignKey("groups.id"))
    until = Column(DateTime)  # When the mute expires
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

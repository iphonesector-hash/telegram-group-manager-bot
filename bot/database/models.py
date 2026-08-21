from sqlalchemy import Column, Integer, BigInteger, String, Boolean, DateTime, ForeignKey, Text, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True)
    username = Column(String, nullable=True)
    first_name = Column(String)

    coins = Column(BigInteger, default=0)
    bank_balance = Column(BigInteger, default=0)
    loan_balance = Column(BigInteger, default=0)
    xp = Column(BigInteger, default=0)
    level = Column(Integer, default=1)
    message_count = Column(BigInteger, default=0)

    last_daily_claim = Column(DateTime, nullable=True)
    vip_until = Column(DateTime, nullable=True)

    is_admin = Column(Boolean, default=False)
    joined_at = Column(DateTime, default=datetime.datetime.utcnow)


class Group(Base):
    __tablename__ = "groups"

    id = Column(BigInteger, primary_key=True)
    title = Column(String)

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

    welcome_enabled = Column(Boolean, default=True)
    welcome_text = Column(Text, default="خوش اومدی به گروه 🌟\nلطفاً قوانین رو رعایت کن.")

    rules = Column(Text, nullable=True)
    rules_enabled = Column(Boolean, default=True)

    antispam_enabled = Column(Boolean, default=True)
    antispam_limit = Column(Integer, default=5)
    economy_enabled = Column(Boolean, default=True)
    ai_enabled = Column(Boolean, default=True)

    prevent_bots = Column(Boolean, default=False)
    new_member_limit = Column(Boolean, default=False)
    approval_mode = Column(Boolean, default=False)
    activity_logging = Column(Boolean, default=True)

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
    until = Column(DateTime)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class Purchase(Base):
    __tablename__ = "purchases"
    __table_args__ = (UniqueConstraint("telegram_payment_charge_id", name="uq_purchase_charge"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    item_id = Column(String, nullable=False)
    amount = Column(BigInteger, nullable=False, default=0)
    telegram_payment_charge_id = Column(String, nullable=True)
    status = Column(String, default="completed")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

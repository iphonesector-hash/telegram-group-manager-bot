from sqlalchemy import Column, Integer, BigInteger, String, Boolean, DateTime, Date, ForeignKey, Text, UniqueConstraint, Index, JSON
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = "isectorbot_users"

    id = Column(BigInteger, primary_key=True)
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=False, default="")
    coins = Column(BigInteger, default=0)
    bank_balance = Column("bank", BigInteger, default=0)
    loan_balance = Column("loan", BigInteger, default=0)
    xp = Column(BigInteger, default=0)
    level = Column(Integer, default=1)
    message_count = Column(BigInteger, default=0)
    last_daily_claim = Column(DateTime(timezone=True), nullable=True)
    vip_until = Column(DateTime(timezone=True), nullable=True)
    is_admin = Column(Boolean, default=False)
    joined_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow)


class Group(Base):
    __tablename__ = "isectorbot_groups"

    id = Column(BigInteger, primary_key=True)
    title = Column(String, nullable=False, default="")
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
    joined_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow)


class Warning(Base):
    __tablename__ = "isectorbot_warnings"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("isectorbot_users.id", ondelete="CASCADE"), nullable=False)
    group_id = Column(BigInteger, ForeignKey("isectorbot_groups.id", ondelete="CASCADE"), nullable=False)
    reason = Column(String, default="بدون دلیل")
    warned_by = Column(BigInteger, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow)


class Mute(Base):
    __tablename__ = "isectorbot_mutes"
    __table_args__ = (UniqueConstraint("user_id", "group_id", name="uq_isectorbot_mute_user_group"),)

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("isectorbot_users.id", ondelete="CASCADE"), nullable=False)
    group_id = Column(BigInteger, ForeignKey("isectorbot_groups.id", ondelete="CASCADE"), nullable=False)
    until = Column("until_at", DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow)


class Purchase(Base):
    __tablename__ = "isectorbot_purchases"
    __table_args__ = (UniqueConstraint("telegram_payment_charge_id", name="uq_isectorbot_purchase_charge"),)

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("isectorbot_users.id", ondelete="CASCADE"), nullable=False)
    item_id = Column(String, nullable=False)
    amount = Column(BigInteger, nullable=False, default=0)
    telegram_payment_charge_id = Column(String, nullable=True)
    status = Column(String, default="completed")
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow)


class AppSetting(Base):
    __tablename__ = "isectorbot_settings"

    key = Column(String, primary_key=True)
    value = Column(JSON, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


class RuntimeState(Base):
    """Small durable state for serverless multi-step Telegram interactions."""
    __tablename__ = "isectorbot_runtime_state"
    scope = Column(String, primary_key=True)
    state_key = Column(String, primary_key=True)
    value = Column(JSON, nullable=False, default=dict)
    updated_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


class Order(Base):
    __tablename__ = "isectorbot_orders"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("isectorbot_users.id", ondelete="CASCADE"), nullable=False)
    item_key = Column(Text, nullable=False)
    item_name = Column(Text, nullable=False)
    price = Column(BigInteger, nullable=False, default=0)
    status = Column(Text, nullable=False, default="pending")
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    metadata_json = Column("metadata", JSON, nullable=False, default=dict)


class Referral(Base):
    __tablename__ = "isectorbot_referrals"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    referrer_id = Column(BigInteger, nullable=False)
    referred_id = Column(BigInteger, nullable=False, unique=True)
    reward = Column(BigInteger, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow)


class GameSession(Base):
    __tablename__ = "isectorbot_game_sessions"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    token_hash = Column(Text, nullable=False, unique=True)
    user_id = Column(BigInteger, ForeignKey("isectorbot_users.id", ondelete="CASCADE"), nullable=False)
    game_key = Column(Text, nullable=False)
    started_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used_at = Column(DateTime(timezone=True), nullable=True)
    client_nonce = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow, nullable=False)


class GameScore(Base):
    __tablename__ = "isectorbot_game_scores"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("isectorbot_users.id", ondelete="CASCADE"), nullable=False)
    game_key = Column(Text, nullable=False)
    score = Column(BigInteger, nullable=False)
    duration_seconds = Column(BigInteger, nullable=False)
    session_id = Column(BigInteger, ForeignKey("isectorbot_game_sessions.id", ondelete="CASCADE"), nullable=False, unique=True)
    verified = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow, nullable=False)


class SectorPet(Base):
    __tablename__ = "isectorbot_sector_pets"

    user_id = Column(BigInteger, ForeignKey("isectorbot_users.id", ondelete="CASCADE"), primary_key=True)
    name = Column(Text, nullable=False, default="سکتور")
    level = Column(Integer, nullable=False, default=1)
    xp = Column(BigInteger, nullable=False, default=0)
    energy = Column(Integer, nullable=False, default=80)
    happiness = Column(Integer, nullable=False, default=80)
    knowledge = Column(Integer, nullable=False, default=0)
    health = Column(Integer, nullable=False, default=100)
    hunger = Column(Integer, nullable=False, default=80)
    cleanliness = Column(Integer, nullable=False, default=80)
    personality = Column(Text, nullable=False, default="کنجکاو")
    room_level = Column(Integer, nullable=False, default=1)
    inventory = Column(JSON, nullable=False, default=dict)
    equipped_item = Column(Text, nullable=True)
    sleeping = Column(Boolean, nullable=False, default=False)
    evolution_path = Column(Text, nullable=True)
    appearance = Column(JSON, nullable=False, default=dict)
    story_chapter = Column(Integer, nullable=False, default=1)
    story_progress = Column(Integer, nullable=False, default=0)
    job = Column(Text, nullable=True)
    job_started_at = Column(DateTime(timezone=True), nullable=True)
    notifications_enabled = Column(Boolean, nullable=False, default=True)
    streak_days = Column(Integer, nullable=False, default=0)
    best_streak = Column(Integer, nullable=False, default=0)
    total_care_days = Column(Integer, nullable=False, default=0)
    last_visit_date = Column(Date, nullable=True)
    evolution_tokens = Column(Integer, nullable=False, default=0)
    last_interaction = Column(DateTime(timezone=True), default=datetime.datetime.utcnow, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow, nullable=False)


class SectorPetAction(Base):
    __tablename__ = "isectorbot_sector_pet_actions"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("isectorbot_users.id", ondelete="CASCADE"), nullable=False)
    action = Column(Text, nullable=False)
    coin_cost = Column(BigInteger, nullable=False, default=0)
    xp_gained = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow, nullable=False)


class SectorPetGame(Base):
    __tablename__ = "isectorbot_sector_pet_games"
    __table_args__ = (Index("ix_sector_pet_games_user_created", "user_id", "created_at"),)

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("isectorbot_users.id", ondelete="CASCADE"), nullable=False)
    game_key = Column(Text, nullable=False)
    score = Column(Integer, nullable=False, default=0)
    reward = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow, nullable=False)


class SectorPetMemory(Base):
    __tablename__ = "isectorbot_sector_pet_memories"
    __table_args__ = (Index("ix_sector_memory_user_created", "user_id", "created_at"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("isectorbot_users.id", ondelete="CASCADE"), nullable=False)
    kind = Column(Text, nullable=False, default="moment")
    title = Column(Text, nullable=False)
    detail = Column(Text, nullable=False, default="")
    importance = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow, nullable=False)


class SectorPetSocial(Base):
    __tablename__ = "isectorbot_sector_pet_social"
    __table_args__ = (UniqueConstraint("actor_id", "target_id", "action", "day_key", name="uq_sector_social_daily"),Index("ix_sector_social_target_created", "target_id", "created_at"))

    id = Column(Integer, primary_key=True, autoincrement=True)
    actor_id = Column(BigInteger, ForeignKey("isectorbot_users.id", ondelete="CASCADE"), nullable=False)
    target_id = Column(BigInteger, ForeignKey("isectorbot_users.id", ondelete="CASCADE"), nullable=False)
    action = Column(Text, nullable=False)
    day_key = Column(Text, nullable=False)
    payload = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow, nullable=False)


class SectorClan(Base):
    __tablename__ = "isectorbot_sector_clans"
    __table_args__ = (Index("ix_sector_clans_owner", "owner_id"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text, nullable=False, unique=True)
    owner_id = Column(BigInteger, ForeignKey("isectorbot_users.id", ondelete="CASCADE"), nullable=False)
    xp = Column(BigInteger, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow, nullable=False)


class SectorClanMember(Base):
    __tablename__ = "isectorbot_sector_clan_members"
    __table_args__ = (UniqueConstraint("user_id", name="uq_sector_clan_user"),Index("ix_sector_clan_members_clan", "clan_id"))

    id = Column(Integer, primary_key=True, autoincrement=True)
    clan_id = Column(Integer, ForeignKey("isectorbot_sector_clans.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(BigInteger, ForeignKey("isectorbot_users.id", ondelete="CASCADE"), nullable=False)
    contribution = Column(BigInteger, nullable=False, default=0)
    joined_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow, nullable=False)


class AIMessage(Base):
    __tablename__ = "isectorbot_ai_messages"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("isectorbot_users.id", ondelete="CASCADE"), nullable=False)
    chat_id = Column(BigInteger, nullable=False)
    role = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow, nullable=False)

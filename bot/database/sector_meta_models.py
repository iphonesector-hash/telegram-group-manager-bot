import datetime
from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, Index, Integer, JSON, Text, UniqueConstraint
from bot.database.models import Base

class SectorWorldBoss(Base):
    __tablename__ = 'isectorbot_sector_world_bosses'
    __table_args__ = (UniqueConstraint('season_key', name='uq_sector_world_boss_season'),)
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    season_key = Column(Text, nullable=False)
    title = Column(Text, nullable=False)
    hp = Column(BigInteger, nullable=False)
    max_hp = Column(BigInteger, nullable=False)
    reward_pool = Column(BigInteger, nullable=False, default=0)
    active = Column(Boolean, nullable=False, default=True)
    started_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow, nullable=False)
    ends_at = Column(DateTime(timezone=True), nullable=False)
    defeated_at = Column(DateTime(timezone=True), nullable=True)

class SectorBossHit(Base):
    __tablename__ = 'isectorbot_sector_boss_hits'
    __table_args__ = (Index('ix_sector_boss_hit_user_created','user_id','created_at'),Index('ix_sector_boss_hit_boss_damage','boss_id','damage'))
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    boss_id = Column(BigInteger, ForeignKey('isectorbot_sector_world_bosses.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(BigInteger, ForeignKey('isectorbot_users.id', ondelete='CASCADE'), nullable=False)
    damage = Column(BigInteger, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow, nullable=False)

class SectorRewardClaim(Base):
    __tablename__ = 'isectorbot_sector_reward_claims'
    __table_args__ = (UniqueConstraint('user_id','claim_key','period_key',name='uq_sector_reward_claim'),Index('ix_sector_reward_claim_user_created','user_id','created_at'))
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('isectorbot_users.id', ondelete='CASCADE'), nullable=False)
    claim_key = Column(Text, nullable=False)
    period_key = Column(Text, nullable=False)
    reward = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow, nullable=False)

class SectorLedger(Base):
    __tablename__ = 'isectorbot_sector_ledger'
    __table_args__ = (Index('ix_sector_ledger_user_created','user_id','created_at'),)
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('isectorbot_users.id', ondelete='CASCADE'), nullable=False)
    kind = Column(Text, nullable=False)
    amount = Column(BigInteger, nullable=False, default=0)
    balance_after = Column(BigInteger, nullable=False, default=0)
    ref_type = Column(Text, nullable=True)
    ref_key = Column(Text, nullable=True)
    metadata_json = Column('metadata', JSON, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow, nullable=False)

class SectorAnalyticsEvent(Base):
    __tablename__ = 'isectorbot_sector_analytics'
    __table_args__ = (Index('ix_sector_analytics_event_created','event','created_at'),Index('ix_sector_analytics_user_created','user_id','created_at'))
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('isectorbot_users.id', ondelete='CASCADE'), nullable=True)
    event = Column(Text, nullable=False)
    context = Column(Text, nullable=False, default='miniapp')
    payload = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow, nullable=False)

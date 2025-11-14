"""SQLAlchemy модели для Asset Service"""
from sqlalchemy import Column, String, Boolean, JSON, Integer, ARRAY, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from backend.asset_service.database import Base
import uuid


class Asset(Base):
    __tablename__ = "assets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticker = Column(String(50), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    asset_type = Column(String(50), nullable=False)  # crypto, stock, commodity, hotel, etc.
    source = Column(String(100))  # источник котировок
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class DataSource(Base):
    __tablename__ = "data_sources"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False)
    source_type = Column(String(50), nullable=False)  # exchange, api, rss, etc.
    config = Column(JSON)  # конфигурация подключения
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AssetConfig(Base):
    __tablename__ = "asset_configs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    asset_id = Column(UUID(as_uuid=True), ForeignKey("assets.id", ondelete="CASCADE"), nullable=False, unique=True)
    forecast_horizons = Column(ARRAY(Integer), default=[1, 7, 30])  # дни
    update_frequency = Column(String(50), default="hourly")  # hourly, daily, etc.
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


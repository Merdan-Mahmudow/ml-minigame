"""SQLAlchemy модели для Forecast Storage"""
from sqlalchemy import Column, String, Numeric, Integer, ForeignKey, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from backend.forecast_storage.database import Base
import uuid


class Forecast(Base):
    __tablename__ = "forecasts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    asset_id = Column(UUID(as_uuid=True), nullable=False)
    model_version_id = Column(UUID(as_uuid=True), nullable=False)
    timestamp_forecasted = Column(DateTime(timezone=True), nullable=False)
    horizon = Column(Integer, nullable=False)  # дни
    point_forecast = Column(Numeric(20, 8), nullable=False)
    low_bound = Column(Numeric(20, 8))
    high_bound = Column(Numeric(20, 8))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index('idx_asset_forecast', 'asset_id', 'timestamp_forecasted'),
        Index('idx_forecasts_created', 'created_at'),
        Index('idx_forecasts_asset_horizon', 'asset_id', 'horizon'),
    )


class ForecastMetric(Base):
    __tablename__ = "forecast_metrics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    forecast_id = Column(UUID(as_uuid=True), ForeignKey("forecasts.id", ondelete="CASCADE"), nullable=False)
    actual_value = Column(Numeric(20, 8))
    error = Column(Numeric(20, 8))
    absolute_error = Column(Numeric(20, 8))
    percentage_error = Column(Numeric(20, 8))
    calculated_at = Column(DateTime(timezone=True), server_default=func.now())


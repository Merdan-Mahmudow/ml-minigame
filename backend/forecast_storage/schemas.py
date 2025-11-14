"""Pydantic схемы для Forecast Storage"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID
from decimal import Decimal


class ForecastBase(BaseModel):
    asset_id: UUID
    model_version_id: UUID
    timestamp_forecasted: datetime
    horizon: int
    point_forecast: Decimal
    low_bound: Optional[Decimal] = None
    high_bound: Optional[Decimal] = None


class ForecastCreate(ForecastBase):
    pass


class ForecastResponse(ForecastBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class ForecastMetricBase(BaseModel):
    forecast_id: UUID
    actual_value: Optional[Decimal] = None
    error: Optional[Decimal] = None
    absolute_error: Optional[Decimal] = None
    percentage_error: Optional[Decimal] = None


class ForecastMetricCreate(ForecastMetricBase):
    pass


class ForecastMetricResponse(ForecastMetricBase):
    id: UUID
    calculated_at: datetime

    class Config:
        from_attributes = True


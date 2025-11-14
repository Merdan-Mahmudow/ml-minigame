"""Pydantic схемы для Asset Service"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class AssetBase(BaseModel):
    ticker: str
    name: str
    asset_type: str
    source: Optional[str] = None


class AssetCreate(AssetBase):
    pass


class AssetUpdate(BaseModel):
    ticker: Optional[str] = None
    name: Optional[str] = None
    asset_type: Optional[str] = None
    source: Optional[str] = None


class AssetResponse(AssetBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AssetConfigBase(BaseModel):
    forecast_horizons: List[int] = [1, 7, 30]
    update_frequency: str = "hourly"
    enabled: bool = True


class AssetConfigCreate(AssetConfigBase):
    asset_id: UUID


class AssetConfigResponse(AssetConfigBase):
    id: UUID
    asset_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DataSourceBase(BaseModel):
    name: str
    source_type: str
    config: Optional[dict] = None
    is_active: bool = True


class DataSourceCreate(DataSourceBase):
    pass


class DataSourceResponse(DataSourceBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


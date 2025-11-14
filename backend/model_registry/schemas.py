"""Pydantic схемы для Model Registry"""
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID
from decimal import Decimal


class ModelBase(BaseModel):
    name: str
    model_type: str
    description: Optional[str] = None


class ModelCreate(ModelBase):
    pass


class ModelResponse(ModelBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class ModelVersionBase(BaseModel):
    version: str
    artifact_path: Optional[str] = None
    training_config: Optional[Dict[str, Any]] = None
    status: str = "archived"


class ModelVersionCreate(ModelVersionBase):
    model_id: UUID


class ModelVersionResponse(ModelVersionBase):
    id: UUID
    model_id: UUID
    trained_at: datetime

    class Config:
        from_attributes = True


class ModelMetricBase(BaseModel):
    metric_name: str
    metric_value: Decimal
    dataset_type: Optional[str] = None


class ModelMetricCreate(ModelMetricBase):
    model_version_id: UUID


class ModelMetricResponse(ModelMetricBase):
    id: UUID
    model_version_id: UUID
    calculated_at: datetime

    class Config:
        from_attributes = True


class ModelVersionWithMetrics(ModelVersionResponse):
    metrics: List[ModelMetricResponse] = []


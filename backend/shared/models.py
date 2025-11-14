"""Общие модели данных для всех сервисов"""
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


class HealthResponse(BaseModel):
    status: str
    service: str
    timestamp: datetime


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None


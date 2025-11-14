"""SQLAlchemy модели для Model Registry"""
from sqlalchemy import Column, String, JSON, ForeignKey, DateTime, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from backend.model_registry.database import Base
import uuid


class Model(Base):
    __tablename__ = "models"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    model_type = Column(String(50), nullable=False)  # lightgbm, catboost, neural_network, etc.
    description = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ModelVersion(Base):
    __tablename__ = "model_versions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_id = Column(UUID(as_uuid=True), ForeignKey("models.id", ondelete="CASCADE"), nullable=False)
    version = Column(String(50), nullable=False)
    artifact_path = Column(String(500))  # путь в S3
    training_config = Column(JSON)  # конфигурация обучения
    status = Column(String(50), default="archived")  # prod, canary, archived
    trained_at = Column(DateTime(timezone=True), server_default=func.now())


class ModelMetric(Base):
    __tablename__ = "model_metrics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_version_id = Column(UUID(as_uuid=True), ForeignKey("model_versions.id", ondelete="CASCADE"), nullable=False)
    metric_name = Column(String(100), nullable=False)
    metric_value = Column(Numeric(20, 8), nullable=False)
    dataset_type = Column(String(50))  # train, val, test
    calculated_at = Column(DateTime(timezone=True), server_default=func.now())


"""Конфигурация Model Training"""
from backend.shared.config import settings
from pydantic_settings import BaseSettings


class TrainingSettings(BaseSettings):
    FEATURE_PIPELINE_URL: str = "http://feature-pipeline:8005"
    MODEL_REGISTRY_URL: str = "http://model-registry:8007"
    MINIO_ENDPOINT: str = settings.MINIO_ENDPOINT
    MINIO_ACCESS_KEY: str = settings.MINIO_ACCESS_KEY
    MINIO_SECRET_KEY: str = settings.MINIO_SECRET_KEY
    MINIO_BUCKET_MODELS: str = settings.MINIO_BUCKET_MODELS
    MINIO_BUCKET_FEATURES: str = settings.MINIO_BUCKET_FEATURES
    
    # Параметры обучения
    TRAIN_TEST_SPLIT: float = 0.2
    VALIDATION_SPLIT: float = 0.1
    RANDOM_STATE: int = 42
    
    class Config:
        env_file = ".env"
        case_sensitive = True


training_settings = TrainingSettings()


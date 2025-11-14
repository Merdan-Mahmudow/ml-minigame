"""Конфигурация Forecast Service"""
from backend.shared.config import settings
from pydantic_settings import BaseSettings


class ForecastSettings(BaseSettings):
    MODEL_REGISTRY_URL: str = "http://model-registry:8007"
    FEATURE_PIPELINE_URL: str = "http://feature-pipeline:8005"
    FORECAST_STORAGE_URL: str = "http://forecast-storage:8008"
    
    MINIO_ENDPOINT: str = settings.MINIO_ENDPOINT
    MINIO_ACCESS_KEY: str = settings.MINIO_ACCESS_KEY
    MINIO_SECRET_KEY: str = settings.MINIO_SECRET_KEY
    MINIO_BUCKET_MODELS: str = settings.MINIO_BUCKET_MODELS
    
    REDIS_HOST: str = settings.REDIS_HOST
    REDIS_PORT: int = settings.REDIS_PORT
    
    # Кеширование моделей в памяти
    MODEL_CACHE_SIZE: int = 10
    
    class Config:
        env_file = ".env"
        case_sensitive = True


forecast_settings = ForecastSettings()


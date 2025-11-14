"""Конфигурация Feature Pipeline"""
from backend.shared.config import settings
from pydantic_settings import BaseSettings


class FeaturePipelineSettings(BaseSettings):
    CLICKHOUSE_HOST: str = settings.CLICKHOUSE_HOST
    CLICKHOUSE_PORT: int = settings.CLICKHOUSE_PORT
    CLICKHOUSE_USER: str = settings.CLICKHOUSE_USER
    CLICKHOUSE_PASSWORD: str = settings.CLICKHOUSE_PASSWORD
    CLICKHOUSE_DB: str = settings.CLICKHOUSE_DB
    
    REDIS_HOST: str = settings.REDIS_HOST
    REDIS_PORT: int = settings.REDIS_PORT
    
    MINIO_ENDPOINT: str = settings.MINIO_ENDPOINT
    MINIO_ACCESS_KEY: str = settings.MINIO_ACCESS_KEY
    MINIO_SECRET_KEY: str = settings.MINIO_SECRET_KEY
    MINIO_BUCKET_FEATURES: str = settings.MINIO_BUCKET_FEATURES
    
    class Config:
        env_file = ".env"
        case_sensitive = True


feature_settings = FeaturePipelineSettings()


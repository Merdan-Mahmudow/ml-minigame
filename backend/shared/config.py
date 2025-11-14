"""Общие настройки конфигурации"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # API Gateway
    API_GATEWAY_HOST: str = "0.0.0.0"
    API_GATEWAY_PORT: int = 8000
    
    # JWT
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Services URLs
    ASSET_SERVICE_URL: str = "http://asset-service:8001"
    FORECAST_SERVICE_URL: str = "http://forecast-service:8002"
    FORECAST_STORAGE_URL: str = "http://forecast-storage:8008"
    MODEL_REGISTRY_URL: str = "http://model-registry:8007"
    ADMIN_SERVICE_URL: str = "http://admin-service:8010"
    
    # Database
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "forecast_user"
    POSTGRES_PASSWORD: str = "forecast_password"
    POSTGRES_DB: str = "forecast_db"
    
    # ClickHouse
    CLICKHOUSE_HOST: str = "clickhouse"
    CLICKHOUSE_PORT: int = 8123
    CLICKHOUSE_USER: str = "forecast_user"
    CLICKHOUSE_PASSWORD: str = "forecast_password"
    CLICKHOUSE_DB: str = "forecast_ts"
    
    # Redis
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    
    # MinIO (S3)
    MINIO_ENDPOINT: str = "minio:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin123"
    MINIO_BUCKET_RAW_DATA: str = "raw-data"
    MINIO_BUCKET_MODELS: str = "model-artifacts"
    MINIO_BUCKET_FEATURES: str = "feature-store"
    
    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str = "kafka:9092"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()


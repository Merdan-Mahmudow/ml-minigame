"""Конфигурация News Collector"""
from backend.shared.config import settings
from pydantic_settings import BaseSettings


class NewsCollectorSettings(BaseSettings):
    CLICKHOUSE_HOST: str = settings.CLICKHOUSE_HOST
    CLICKHOUSE_PORT: int = settings.CLICKHOUSE_PORT
    CLICKHOUSE_USER: str = settings.CLICKHOUSE_USER
    CLICKHOUSE_PASSWORD: str = settings.CLICKHOUSE_PASSWORD
    CLICKHOUSE_DB: str = settings.CLICKHOUSE_DB
    
    MINIO_ENDPOINT: str = settings.MINIO_ENDPOINT
    MINIO_ACCESS_KEY: str = settings.MINIO_ACCESS_KEY
    MINIO_SECRET_KEY: str = settings.MINIO_SECRET_KEY
    MINIO_BUCKET_RAW_DATA: str = settings.MINIO_BUCKET_RAW_DATA
    
    KAFKA_BOOTSTRAP_SERVERS: str = settings.KAFKA_BOOTSTRAP_SERVERS
    KAFKA_TOPIC_NEWS: str = "news-collection-tasks"
    
    ASSET_SERVICE_URL: str = settings.ASSET_SERVICE_URL
    
    COLLECTION_INTERVAL_MINUTES: int = 30  # Интервал сбора новостей
    
    # News API (опционально)
    NEWS_API_KEY: str = ""  # Заполнить при использовании News API
    
    class Config:
        env_file = ".env"
        case_sensitive = True


news_settings = NewsCollectorSettings()


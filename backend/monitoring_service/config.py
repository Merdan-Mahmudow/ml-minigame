"""Конфигурация Monitoring Service"""
from backend.shared.config import settings
from pydantic_settings import BaseSettings


class MonitoringSettings(BaseSettings):
    FORECAST_STORAGE_URL: str = "http://forecast-storage:8008"
    CLICKHOUSE_HOST: str = settings.CLICKHOUSE_HOST
    CLICKHOUSE_PORT: int = settings.CLICKHOUSE_PORT
    CLICKHOUSE_USER: str = settings.CLICKHOUSE_USER
    CLICKHOUSE_PASSWORD: str = settings.CLICKHOUSE_PASSWORD
    CLICKHOUSE_DB: str = settings.CLICKHOUSE_DB
    
    # Пороги для алертов
    MAE_THRESHOLD: float = 10.0
    MAPE_THRESHOLD: float = 5.0
    RMSE_THRESHOLD: float = 15.0
    
    # Настройки алертов
    ALERT_EMAIL: str = ""
    ALERT_SLACK_WEBHOOK: str = ""
    ALERT_TELEGRAM_BOT_TOKEN: str = ""
    ALERT_TELEGRAM_CHAT_ID: str = ""
    
    class Config:
        env_file = ".env"
        case_sensitive = True


monitoring_settings = MonitoringSettings()


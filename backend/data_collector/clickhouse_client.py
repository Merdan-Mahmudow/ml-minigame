"""Клиент для работы с ClickHouse"""
from clickhouse_driver import Client
from backend.data_collector.config import collector_settings
from typing import List, Dict, Any
from datetime import datetime


class ClickHouseClient:
    def __init__(self):
        self.client = Client(
            host=collector_settings.CLICKHOUSE_HOST,
            port=collector_settings.CLICKHOUSE_PORT,
            user=collector_settings.CLICKHOUSE_USER,
            password=collector_settings.CLICKHOUSE_PASSWORD,
            database=collector_settings.CLICKHOUSE_DB
        )
    
    def insert_market_data(self, data: List[Dict[str, Any]]):
        """Вставка рыночных данных"""
        if not data:
            return
        
        self.client.execute(
            """
            INSERT INTO market_data 
            (asset_id, timestamp, open, high, low, close, volume, source, raw_data)
            VALUES
            """,
            data
        )
    
    def get_latest_timestamp(self, asset_id: str) -> datetime:
        """Получение последнего timestamp для актива"""
        result = self.client.execute(
            """
            SELECT max(timestamp) 
            FROM market_data 
            WHERE asset_id = %s
            """,
            [asset_id]
        )
        if result and result[0][0]:
            return result[0][0]
        return datetime(2020, 1, 1)  # Начальная дата по умолчанию


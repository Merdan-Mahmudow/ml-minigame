"""Клиент для работы с ClickHouse (новости)"""
from clickhouse_driver import Client
from backend.news_collector.config import news_settings
from typing import List, Dict, Any


class NewsClickHouseClient:
    def __init__(self):
        self.client = Client(
            host=news_settings.CLICKHOUSE_HOST,
            port=news_settings.CLICKHOUSE_PORT,
            user=news_settings.CLICKHOUSE_USER,
            password=news_settings.CLICKHOUSE_PASSWORD,
            database=news_settings.CLICKHOUSE_DB
        )
    
    def insert_news(self, data: List[Dict[str, Any]]):
        """Вставка новостей"""
        if not data:
            return
        
        self.client.execute(
            """
            INSERT INTO news_feed 
            (id, asset_id, timestamp, source, title, text, url, sentiment, importance, raw_data)
            VALUES
            """,
            data
        )


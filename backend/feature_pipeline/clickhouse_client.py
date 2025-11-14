"""Клиент для работы с ClickHouse"""
from clickhouse_driver import Client
from backend.feature_pipeline.config import feature_settings
import pandas as pd
from typing import List, Dict, Any
from datetime import datetime


class FeatureClickHouseClient:
    def __init__(self):
        self.client = Client(
            host=feature_settings.CLICKHOUSE_HOST,
            port=feature_settings.CLICKHOUSE_PORT,
            user=feature_settings.CLICKHOUSE_USER,
            password=feature_settings.CLICKHOUSE_PASSWORD,
            database=feature_settings.CLICKHOUSE_DB
        )
    
    def get_market_data(self, asset_id: str, start_time: datetime, end_time: datetime) -> pd.DataFrame:
        """Получение рыночных данных"""
        query = """
        SELECT 
            timestamp,
            open,
            high,
            low,
            close,
            volume
        FROM market_data
        WHERE asset_id = %s
        AND timestamp >= %s
        AND timestamp <= %s
        ORDER BY timestamp
        """
        
        result = self.client.execute(query, [asset_id, start_time, end_time])
        
        if not result:
            return pd.DataFrame()
        
        df = pd.DataFrame(result, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        return df
    
    def get_news_data(self, asset_id: str, start_time: datetime, end_time: datetime) -> pd.DataFrame:
        """Получение новостей"""
        query = """
        SELECT 
            timestamp,
            sentiment,
            importance
        FROM news_feed
        WHERE asset_id = %s
        AND timestamp >= %s
        AND timestamp <= %s
        ORDER BY timestamp
        """
        
        result = self.client.execute(query, [asset_id, start_time, end_time])
        
        if not result:
            return pd.DataFrame()
        
        df = pd.DataFrame(result, columns=['timestamp', 'sentiment', 'importance'])
        return df
    
    def save_features(self, features: List[Dict[str, Any]]):
        """Сохранение фичей в ClickHouse"""
        if not features:
            return
        
        self.client.execute(
            """
            INSERT INTO features 
            (asset_id, timestamp, feature_name, feature_value)
            VALUES
            """,
            features
        )


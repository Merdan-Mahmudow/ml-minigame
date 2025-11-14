"""Online-обработка фичей по запросу"""
from backend.feature_pipeline.clickhouse_client import FeatureClickHouseClient
from backend.feature_pipeline.redis_client import FeatureRedisClient
from backend.feature_pipeline.feature_engineering import FeatureEngineer
from datetime import datetime, timedelta
import pandas as pd
from typing import Dict, Any, Optional


class OnlineFeatureProcessor:
    def __init__(self):
        self.clickhouse = FeatureClickHouseClient()
        self.redis = FeatureRedisClient()
        self.feature_engineer = FeatureEngineer()
    
    def compute_features(self, asset_id: str, lookback_hours: int = 24) -> Optional[Dict[str, Any]]:
        """Вычисление фичей онлайн"""
        # Проверка кеша в Redis
        cached = self.redis.get_latest_features(asset_id)
        if cached:
            cached_time = datetime.fromisoformat(cached.get('timestamp', ''))
            if (datetime.utcnow() - cached_time).total_seconds() < 3600:  # Кеш актуален менее часа
                return cached
        
        # Получение данных из ClickHouse
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=lookback_hours)
        
        market_data = self.clickhouse.get_market_data(asset_id, start_time, end_time)
        if market_data.empty:
            return None
        
        news_data = self.clickhouse.get_news_data(asset_id, start_time, end_time)
        
        # Вычисление фичей
        features_df = self.feature_engineer.compute_features(market_data, news_data)
        
        if features_df.empty:
            return None
        
        # Взять последнюю строку
        latest_row = features_df.iloc[-1]
        features_dict = latest_row.to_dict()
        
        # Сохранение в Redis
        latest_timestamp = features_df['timestamp'].max()
        self.redis.save_features(asset_id, features_dict, latest_timestamp)
        
        return features_dict


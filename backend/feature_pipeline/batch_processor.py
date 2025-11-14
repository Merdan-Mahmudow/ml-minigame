"""Batch-обработка фичей"""
from backend.feature_pipeline.clickhouse_client import FeatureClickHouseClient
from backend.feature_pipeline.redis_client import FeatureRedisClient
from backend.feature_pipeline.s3_client import FeatureS3Client
from backend.feature_pipeline.feature_engineering import FeatureEngineer
from datetime import datetime, timedelta
import pandas as pd
from typing import List, Dict, Any


class BatchFeatureProcessor:
    def __init__(self):
        self.clickhouse = FeatureClickHouseClient()
        self.redis = FeatureRedisClient()
        self.s3 = FeatureS3Client()
        self.feature_engineer = FeatureEngineer()
    
    def process_asset(self, asset_id: str, start_time: datetime, end_time: datetime):
        """Обработка фичей для актива"""
        # Получение данных
        market_data = self.clickhouse.get_market_data(asset_id, start_time, end_time)
        if market_data.empty:
            print(f"No market data for {asset_id}")
            return
        
        news_data = self.clickhouse.get_news_data(asset_id, start_time, end_time)
        
        # Вычисление фичей
        features_df = self.feature_engineer.compute_features(market_data, news_data)
        
        # Удаление NaN
        features_df = features_df.dropna()
        
        if features_df.empty:
            print(f"No features computed for {asset_id}")
            return
        
        # Сохранение в S3 (Parquet)
        latest_timestamp = features_df['timestamp'].max()
        self.s3.save_features_parquet(asset_id, features_df, latest_timestamp)
        
        # Сохранение последних фичей в Redis
        latest_row = features_df.iloc[-1]
        features_dict = latest_row.to_dict()
        self.redis.save_features(asset_id, features_dict, latest_timestamp)
        
        # Сохранение в ClickHouse (опционально, для аналитики)
        clickhouse_features = []
        for _, row in features_df.iterrows():
            for col in features_df.columns:
                if col != 'timestamp':
                    clickhouse_features.append({
                        'asset_id': asset_id,
                        'timestamp': row['timestamp'],
                        'feature_name': col,
                        'feature_value': float(row[col]) if pd.notna(row[col]) else 0.0
                    })
        
        if clickhouse_features:
            self.clickhouse.save_features(clickhouse_features)
        
        print(f"Processed {len(features_df)} feature rows for {asset_id}")


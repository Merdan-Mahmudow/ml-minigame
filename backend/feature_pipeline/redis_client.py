"""Клиент для работы с Redis (Feature Store)"""
import redis
import json
from backend.feature_pipeline.config import feature_settings
from typing import Dict, Any, Optional
from datetime import datetime


class FeatureRedisClient:
    def __init__(self):
        self.redis_client = redis.Redis(
            host=feature_settings.REDIS_HOST,
            port=feature_settings.REDIS_PORT,
            decode_responses=True
        )
    
    def save_features(self, asset_id: str, features: Dict[str, Any], timestamp: datetime):
        """Сохранение фичей в Redis"""
        key = f"features:{asset_id}:{timestamp.isoformat()}"
        self.redis_client.setex(
            key,
            3600 * 24,  # TTL 24 часа
            json.dumps(features)
        )
    
    def get_latest_features(self, asset_id: str) -> Optional[Dict[str, Any]]:
        """Получение последних фичей для актива"""
        # Поиск последнего ключа
        pattern = f"features:{asset_id}:*"
        keys = self.redis_client.keys(pattern)
        
        if not keys:
            return None
        
        # Сортировка по timestamp
        keys.sort(reverse=True)
        latest_key = keys[0]
        
        data = self.redis_client.get(latest_key)
        if data:
            return json.loads(data)
        return None
    
    def get_features_by_timestamp(self, asset_id: str, timestamp: datetime) -> Optional[Dict[str, Any]]:
        """Получение фичей по timestamp"""
        key = f"features:{asset_id}:{timestamp.isoformat()}"
        data = self.redis_client.get(key)
        if data:
            return json.loads(data)
        return None


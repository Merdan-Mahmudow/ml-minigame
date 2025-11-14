"""Мок-коллектор для тестирования (заглушка)"""
from backend.data_collector.collectors.base import BaseCollector
from typing import Dict, Any, List
from datetime import datetime, timedelta
import random


class MockCollector(BaseCollector):
    """Мок-коллектор, генерирующий тестовые данные"""
    
    def fetch_data(self, asset_id: str, start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        """Генерация тестовых данных"""
        data = []
        current_time = start_time
        base_price = 100.0
        
        while current_time <= end_time:
            # Генерация OHLCV данных
            open_price = base_price + random.uniform(-5, 5)
            high_price = open_price + random.uniform(0, 3)
            low_price = open_price - random.uniform(0, 3)
            close_price = random.uniform(low_price, high_price)
            volume = random.uniform(1000, 10000)
            
            data.append({
                "timestamp": current_time,
                "open": open_price,
                "high": high_price,
                "low": low_price,
                "close": close_price,
                "volume": volume
            })
            
            base_price = close_price
            current_time += timedelta(hours=1)
        
        return data
    
    def normalize_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Нормализация данных"""
        return {
            "timestamp": raw_data["timestamp"],
            "open": float(raw_data["open"]),
            "high": float(raw_data["high"]),
            "low": float(raw_data["low"]),
            "close": float(raw_data["close"]),
            "volume": float(raw_data["volume"])
        }


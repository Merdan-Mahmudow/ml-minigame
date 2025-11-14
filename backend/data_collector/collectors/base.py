"""Базовый класс для коллекторов данных"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from datetime import datetime


class BaseCollector(ABC):
    """Базовый класс для всех коллекторов"""
    
    @abstractmethod
    def fetch_data(self, asset_id: str, start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        """Получение данных из внешнего источника"""
        pass
    
    @abstractmethod
    def normalize_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Нормализация данных в единый формат"""
        pass


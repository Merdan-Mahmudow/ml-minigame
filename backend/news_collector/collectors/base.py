"""Базовый класс для коллекторов новостей"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from datetime import datetime


class BaseNewsCollector(ABC):
    """Базовый класс для всех коллекторов новостей"""
    
    @abstractmethod
    def fetch_news(self, query: str, start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        """Получение новостей из внешнего источника"""
        pass
    
    @abstractmethod
    def normalize_news(self, raw_news: Dict[str, Any]) -> Dict[str, Any]:
        """Нормализация новостей в единый формат"""
        pass


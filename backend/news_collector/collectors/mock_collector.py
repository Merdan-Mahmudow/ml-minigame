"""Мок-коллектор новостей для тестирования"""
from backend.news_collector.collectors.base import BaseNewsCollector
from typing import List, Dict, Any
from datetime import datetime, timedelta
import random
import uuid


class MockNewsCollector(BaseNewsCollector):
    """Мок-коллектор, генерирующий тестовые новости"""
    
    def fetch_news(self, query: str, start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        """Генерация тестовых новостей"""
        news = []
        current_time = start_time
        
        # Генерация 1-3 новостей в день
        while current_time <= end_time:
            num_news = random.randint(1, 3)
            for _ in range(num_news):
                sentiment = random.uniform(-1, 1)  # -1 негатив, 1 позитив
                importance = random.uniform(0, 1)
                
                titles = [
                    f"Breaking: {query} shows significant movement",
                    f"Analysis: {query} market trends",
                    f"Update: {query} price action",
                    f"News: {query} reaches new levels",
                    f"Report: {query} market analysis"
                ]
                
                news.append({
                    "id": str(uuid.uuid4()),
                    "timestamp": current_time + timedelta(hours=random.randint(0, 23)),
                    "source": "mock-news",
                    "title": random.choice(titles),
                    "text": f"This is a mock news article about {query}. Market conditions are changing.",
                    "url": f"https://example.com/news/{uuid.uuid4()}",
                    "sentiment": sentiment,
                    "importance": importance
                })
            
            current_time += timedelta(days=1)
        
        return news
    
    def normalize_news(self, raw_news: Dict[str, Any]) -> Dict[str, Any]:
        """Нормализация новостей"""
        return {
            "id": raw_news.get("id", str(uuid.uuid4())),
            "timestamp": raw_news["timestamp"],
            "source": raw_news.get("source", "unknown"),
            "title": raw_news.get("title", ""),
            "text": raw_news.get("text", ""),
            "url": raw_news.get("url", ""),
            "sentiment": float(raw_news.get("sentiment", 0.0)),
            "importance": float(raw_news.get("importance", 0.5))
        }


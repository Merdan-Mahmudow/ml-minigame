"""RSS коллектор новостей"""
from backend.news_collector.collectors.base import BaseNewsCollector
from typing import List, Dict, Any
from datetime import datetime
import feedparser
import uuid


class RSSCollector(BaseNewsCollector):
    """Коллектор новостей из RSS"""
    
    def __init__(self, rss_url: str):
        self.rss_url = rss_url
    
    def fetch_news(self, query: str, start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        """Получение новостей из RSS"""
        try:
            feed = feedparser.parse(self.rss_url)
            news = []
            
            for entry in feed.entries:
                # Парсинг даты
                entry_time = datetime(*entry.published_parsed[:6]) if hasattr(entry, 'published_parsed') else datetime.utcnow()
                
                if start_time <= entry_time <= end_time:
                    news.append({
                        "id": str(uuid.uuid4()),
                        "timestamp": entry_time,
                        "source": "rss",
                        "title": entry.get("title", ""),
                        "text": entry.get("summary", ""),
                        "url": entry.get("link", ""),
                        "sentiment": 0.0,  # Будет вычислено позже
                        "importance": 0.5
                    })
            
            return news
        except Exception as e:
            print(f"Error fetching RSS: {e}")
            return []
    
    def normalize_news(self, raw_news: Dict[str, Any]) -> Dict[str, Any]:
        """Нормализация новостей"""
        return {
            "id": raw_news.get("id", str(uuid.uuid4())),
            "timestamp": raw_news["timestamp"],
            "source": raw_news.get("source", "rss"),
            "title": raw_news.get("title", ""),
            "text": raw_news.get("text", ""),
            "url": raw_news.get("url", ""),
            "sentiment": float(raw_news.get("sentiment", 0.0)),
            "importance": float(raw_news.get("importance", 0.5))
        }


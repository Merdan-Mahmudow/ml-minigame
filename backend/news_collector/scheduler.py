"""Scheduler для создания задач сбора новостей"""
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from kafka import KafkaProducer
import json
from backend.news_collector.config import news_settings
import httpx
from datetime import datetime


class NewsCollectionScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.producer = KafkaProducer(
            bootstrap_servers=news_settings.KAFKA_BOOTSTRAP_SERVERS.split(','),
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        self.http_client = httpx.AsyncClient()
    
    async def get_active_assets(self):
        """Получение списка активных активов"""
        try:
            url = f"{news_settings.ASSET_SERVICE_URL}/assets"
            response = await self.http_client.get(url, params={"limit": 1000})
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Error fetching assets: {e}")
        return []
    
    async def create_collection_tasks(self):
        """Создание задач для сбора новостей"""
        assets = await self.get_active_assets()
        print(f"Creating news collection tasks for {len(assets)} assets")
        
        for asset in assets:
            task = {
                "asset_id": str(asset["id"]),
                "ticker": asset.get("ticker"),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            self.producer.send(news_settings.KAFKA_TOPIC_NEWS, task)
            print(f"Created news task for asset {asset.get('ticker')}")
        
        self.producer.flush()
    
    def start(self):
        """Запуск scheduler"""
        # Запуск каждые N минут
        self.scheduler.add_job(
            self.create_collection_tasks,
            'interval',
            minutes=news_settings.COLLECTION_INTERVAL_MINUTES
        )
        self.scheduler.start()
        print(f"News Scheduler started with interval {news_settings.COLLECTION_INTERVAL_MINUTES} minutes")
    
    def stop(self):
        """Остановка scheduler"""
        self.scheduler.shutdown()
        self.producer.close()
    
    async def close(self):
        """Закрытие соединений"""
        await self.http_client.aclose()


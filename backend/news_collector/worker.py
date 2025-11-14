"""Worker для обработки задач сбора новостей"""
import asyncio
import json
from kafka import KafkaConsumer
from backend.news_collector.config import news_settings
from backend.news_collector.clickhouse_client import NewsClickHouseClient
from backend.news_collector.s3_client import NewsS3Client
from backend.news_collector.collectors import MockNewsCollector
from datetime import datetime, timedelta
import httpx


class NewsCollectorWorker:
    def __init__(self):
        self.clickhouse = NewsClickHouseClient()
        self.s3 = NewsS3Client()
        self.collector = MockNewsCollector()
        self.consumer = KafkaConsumer(
            news_settings.KAFKA_TOPIC_NEWS,
            bootstrap_servers=news_settings.KAFKA_BOOTSTRAP_SERVERS.split(','),
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            group_id='news-collector-workers'
        )
        self.http_client = httpx.AsyncClient()
    
    async def get_assets(self):
        """Получение списка активов"""
        try:
            url = f"{news_settings.ASSET_SERVICE_URL}/assets"
            response = await self.http_client.get(url, params={"limit": 1000})
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Error fetching assets: {e}")
        return []
    
    async def process_task(self, task: dict):
        """Обработка задачи сбора новостей"""
        asset_id = task.get("asset_id")
        ticker = task.get("ticker")
        query = ticker or asset_id
        
        if not query:
            print("Task missing asset_id or ticker")
            return
        
        # Определение временного диапазона (последние 24 часа)
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=1)
        
        # Сбор новостей
        print(f"Collecting news for {query} from {start_time} to {end_time}")
        raw_news_list = self.collector.fetch_news(query, start_time, end_time)
        
        if not raw_news_list:
            print(f"No new news for {query}")
            return
        
        # Нормализация и сохранение
        clickhouse_data = []
        for raw_news in raw_news_list:
            normalized = self.collector.normalize_news(raw_news)
            
            # Сохранение в S3
            s3_key = self.s3.save_raw_news(normalized["source"], raw_news, normalized["timestamp"])
            
            # Подготовка данных для ClickHouse
            clickhouse_data.append({
                "id": normalized["id"],
                "asset_id": asset_id or "",
                "timestamp": normalized["timestamp"],
                "source": normalized["source"],
                "title": normalized["title"],
                "text": normalized["text"],
                "url": normalized["url"],
                "sentiment": normalized["sentiment"],
                "importance": normalized["importance"],
                "raw_data": json.dumps(raw_news)
            })
        
        # Вставка в ClickHouse
        if clickhouse_data:
            self.clickhouse.insert_news(clickhouse_data)
            print(f"Inserted {len(clickhouse_data)} news items for {query}")
    
    async def run(self):
        """Основной цикл worker"""
        print("News Collector Worker started")
        for message in self.consumer:
            try:
                task = message.value
                await self.process_task(task)
            except Exception as e:
                print(f"Error processing task: {e}")
    
    async def close(self):
        """Закрытие соединений"""
        self.consumer.close()
        await self.http_client.aclose()


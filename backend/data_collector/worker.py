"""Worker для обработки задач сбора данных"""
import asyncio
import json
from kafka import KafkaConsumer
from backend.data_collector.config import collector_settings
from backend.data_collector.clickhouse_client import ClickHouseClient
from backend.data_collector.s3_client import S3Client
from backend.data_collector.collectors import MockCollector
from datetime import datetime, timedelta
import httpx


class DataCollectorWorker:
    def __init__(self):
        self.clickhouse = ClickHouseClient()
        self.s3 = S3Client()
        self.collector = MockCollector()
        self.consumer = KafkaConsumer(
            collector_settings.KAFKA_TOPIC_MARKET_DATA,
            bootstrap_servers=collector_settings.KAFKA_BOOTSTRAP_SERVERS.split(','),
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            group_id='data-collector-workers'
        )
        self.http_client = httpx.AsyncClient()
    
    async def get_asset_info(self, asset_id: str):
        """Получение информации об активе"""
        try:
            url = f"{collector_settings.ASSET_SERVICE_URL}/assets/{asset_id}"
            response = await self.http_client.get(url)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Error fetching asset info: {e}")
        return None
    
    async def process_task(self, task: dict):
        """Обработка задачи сбора данных"""
        asset_id = task.get("asset_id")
        if not asset_id:
            print("Task missing asset_id")
            return
        
        # Получение информации об активе
        asset_info = await self.get_asset_info(asset_id)
        if not asset_info:
            print(f"Asset {asset_id} not found")
            return
        
        # Получение последнего timestamp
        last_timestamp = self.clickhouse.get_latest_timestamp(asset_id)
        end_time = datetime.utcnow()
        
        # Сбор данных
        print(f"Collecting data for {asset_id} from {last_timestamp} to {end_time}")
        raw_data_list = self.collector.fetch_data(asset_id, last_timestamp, end_time)
        
        if not raw_data_list:
            print(f"No new data for {asset_id}")
            return
        
        # Нормализация и сохранение
        clickhouse_data = []
        for raw_data in raw_data_list:
            normalized = self.collector.normalize_data(raw_data)
            
            # Сохранение в S3
            s3_key = self.s3.save_raw_data(asset_id, raw_data, normalized["timestamp"])
            
            # Подготовка данных для ClickHouse
            clickhouse_data.append({
                "asset_id": asset_id,
                "timestamp": normalized["timestamp"],
                "open": normalized["open"],
                "high": normalized["high"],
                "low": normalized["low"],
                "close": normalized["close"],
                "volume": normalized["volume"],
                "source": asset_info.get("source", "unknown"),
                "raw_data": json.dumps(raw_data)
            })
        
        # Вставка в ClickHouse
        if clickhouse_data:
            self.clickhouse.insert_market_data(clickhouse_data)
            print(f"Inserted {len(clickhouse_data)} records for {asset_id}")
    
    async def run(self):
        """Основной цикл worker"""
        print("Data Collector Worker started")
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


"""Клиент для работы с S3 (новости)"""
import boto3
from botocore.config import Config
from backend.news_collector.config import news_settings
import json
from datetime import datetime
from typing import Dict, Any


class NewsS3Client:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            endpoint_url=f"http://{news_settings.MINIO_ENDPOINT}",
            aws_access_key_id=news_settings.MINIO_ACCESS_KEY,
            aws_secret_access_key=news_settings.MINIO_SECRET_KEY,
            config=Config(signature_version='s3v4')
        )
        self.bucket = news_settings.MINIO_BUCKET_RAW_DATA
    
    def save_raw_news(self, source: str, data: Dict[str, Any], timestamp: datetime):
        """Сохранение сырых новостей в S3"""
        year = timestamp.year
        month = timestamp.month
        day = timestamp.day
        
        key = f"news/{source}/{year}/{month:02d}/{day:02d}/{timestamp.isoformat()}.json"
        
        self.s3_client.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=json.dumps(data),
            ContentType='application/json'
        )
        
        return key


"""Клиент для работы с S3 (MinIO)"""
import boto3
from botocore.config import Config
from backend.data_collector.config import collector_settings
import json
from datetime import datetime
from typing import Dict, Any


class S3Client:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            endpoint_url=f"http://{collector_settings.MINIO_ENDPOINT}",
            aws_access_key_id=collector_settings.MINIO_ACCESS_KEY,
            aws_secret_access_key=collector_settings.MINIO_SECRET_KEY,
            config=Config(signature_version='s3v4')
        )
        self.bucket = collector_settings.MINIO_BUCKET_RAW_DATA
    
    def save_raw_data(self, asset_id: str, data: Dict[str, Any], timestamp: datetime):
        """Сохранение сырых данных в S3"""
        year = timestamp.year
        month = timestamp.month
        day = timestamp.day
        
        key = f"market_data/{asset_id}/{year}/{month:02d}/{day:02d}/{timestamp.isoformat()}.json"
        
        self.s3_client.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=json.dumps(data),
            ContentType='application/json'
        )
        
        return key


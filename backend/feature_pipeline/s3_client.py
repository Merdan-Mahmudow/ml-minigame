"""Клиент для работы с S3 (сохранение фичей)"""
import boto3
from botocore.config import Config
from backend.feature_pipeline.config import feature_settings
import pandas as pd
from datetime import datetime
from io import BytesIO


class FeatureS3Client:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            endpoint_url=f"http://{feature_settings.MINIO_ENDPOINT}",
            aws_access_key_id=feature_settings.MINIO_ACCESS_KEY,
            aws_secret_access_key=feature_settings.MINIO_SECRET_KEY,
            config=Config(signature_version='s3v4')
        )
        self.bucket = feature_settings.MINIO_BUCKET_FEATURES
    
    def save_features_parquet(self, asset_id: str, df: pd.DataFrame, timestamp: datetime):
        """Сохранение фичей в формате Parquet"""
        year = timestamp.year
        month = timestamp.month
        day = timestamp.day
        
        key = f"features/{asset_id}/{year}/{month:02d}/{day:02d}/features.parquet"
        
        buffer = BytesIO()
        df.to_parquet(buffer, index=False)
        buffer.seek(0)
        
        self.s3_client.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=buffer.getvalue(),
            ContentType='application/octet-stream'
        )
        
        return key


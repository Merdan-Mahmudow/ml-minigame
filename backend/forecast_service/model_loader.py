"""Загрузчик моделей из Model Registry и S3"""
import httpx
import boto3
from botocore.config import Config
from io import BytesIO
import lightgbm as lgb
import torch
from typing import Dict, Any, Optional
from backend.forecast_service.config import forecast_settings
from backend.model_training.trainers import LightGBMTrainer, NeuralTrainer
from uuid import UUID


class ModelLoader:
    """Загрузчик и кеширование моделей"""
    
    def __init__(self):
        self.http_client = httpx.AsyncClient()
        self.s3_client = boto3.client(
            's3',
            endpoint_url=f"http://{forecast_settings.MINIO_ENDPOINT}",
            aws_access_key_id=forecast_settings.MINIO_ACCESS_KEY,
            aws_secret_access_key=forecast_settings.MINIO_SECRET_KEY,
            config=Config(signature_version='s3v4')
        )
        self.model_cache: Dict[str, Any] = {}
        self.lightgbm_trainer = LightGBMTrainer()
    
    async def get_prod_model_version(self, model_id: UUID) -> Dict[str, Any]:
        """Получение продакшн-версии модели из Model Registry"""
        url = f"{forecast_settings.MODEL_REGISTRY_URL}/models/{model_id}/versions/prod"
        response = await self.http_client.get(url)
        if response.status_code == 200:
            return response.json()
        raise ValueError(f"No production model found for {model_id}")
    
    async def load_model_from_s3(self, artifact_path: str, model_type: str) -> Any:
        """Загрузка модели из S3"""
        # Парсинг пути S3
        bucket = forecast_settings.MINIO_BUCKET_MODELS
        key = artifact_path.replace(f"s3://{bucket}/", "").lstrip("/")
        
        # Загрузка из S3
        response = self.s3_client.get_object(Bucket=bucket, Key=key)
        model_bytes = response['Body'].read()
        
        # Десериализация в зависимости от типа
        if model_type == "lightgbm":
            buffer = BytesIO(model_bytes)
            model = lgb.Booster(model_file=buffer)
            return model
        elif model_type == "neural":
            # Для нейросетевых моделей нужен input_size
            # В реальной реализации это должно храниться в метаданных модели
            buffer = BytesIO(model_bytes)
            state_dict = torch.load(buffer, map_location='cpu')
            # Создание модели с правильной архитектурой
            # Здесь упрощенно - в реальности нужна полная архитектура
            from backend.model_training.trainers.neural_trainer import SimpleTimeSeriesNN
            input_size = 10  # Должно быть из метаданных
            model = SimpleTimeSeriesNN(input_size=input_size)
            model.load_state_dict(state_dict)
            model.eval()
            return model
        else:
            raise ValueError(f"Unknown model type: {model_type}")
    
    async def get_model(self, model_id: UUID, use_cache: bool = True) -> Any:
        """Получение модели (с кешированием)"""
        cache_key = str(model_id)
        
        # Проверка кеша
        if use_cache and cache_key in self.model_cache:
            return self.model_cache[cache_key]
        
        # Получение информации о модели
        model_version = await self.get_prod_model_version(model_id)
        artifact_path = model_version.get("artifact_path")
        model_type = model_version.get("training_config", {}).get("model_type", "lightgbm")
        
        if not artifact_path:
            raise ValueError("Model artifact path not found")
        
        # Загрузка модели
        model = await self.load_model_from_s3(artifact_path, model_type)
        
        # Кеширование
        if use_cache:
            if len(self.model_cache) >= forecast_settings.MODEL_CACHE_SIZE:
                # Удаление самого старого элемента (FIFO)
                oldest_key = next(iter(self.model_cache))
                del self.model_cache[oldest_key]
            self.model_cache[cache_key] = model
        
        return model
    
    async def close(self):
        """Закрытие соединений"""
        await self.http_client.aclose()


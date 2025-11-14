"""Пайплайн обучения моделей"""
import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple
from datetime import datetime
import httpx
import boto3
from botocore.config import Config
from io import BytesIO
import torch
from backend.model_training.config import training_settings
from backend.model_training.trainers import LightGBMTrainer, NeuralTrainer
from sklearn.metrics import mean_absolute_error, mean_squared_error, mean_absolute_percentage_error


class TrainingPipeline:
    """Пайплайн для обучения моделей"""
    
    def __init__(self):
        self.http_client = httpx.AsyncClient()
        self.s3_client = boto3.client(
            's3',
            endpoint_url=f"http://{training_settings.MINIO_ENDPOINT}",
            aws_access_key_id=training_settings.MINIO_ACCESS_KEY,
            aws_secret_access_key=training_settings.MINIO_SECRET_KEY,
            config=Config(signature_version='s3v4')
        )
    
    async def load_features(self, asset_id: str, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Загрузка фичей из Feature Pipeline"""
        # В реальной реализации здесь будет загрузка из S3/ClickHouse
        # Для примера используем мок-данные
        dates = pd.date_range(start_date, end_date, freq='H')
        n_samples = len(dates)
        
        # Генерация тестовых фичей
        np.random.seed(42)
        features = pd.DataFrame({
            'timestamp': dates,
            'close_lag_1': np.random.randn(n_samples) * 10 + 100,
            'close_lag_2': np.random.randn(n_samples) * 10 + 100,
            'close_ma_5': np.random.randn(n_samples) * 10 + 100,
            'close_ma_10': np.random.randn(n_samples) * 10 + 100,
            'close_volatility_5': np.abs(np.random.randn(n_samples)),
            'news_count': np.random.randint(0, 10, n_samples),
            'avg_sentiment': np.random.uniform(-1, 1, n_samples),
        })
        
        # Генерация целевой переменной (цена через N дней)
        features['target'] = features['close_lag_1'] + np.random.randn(n_samples) * 2
        
        return features
    
    def prepare_data(self, df: pd.DataFrame, target_col: str = 'target', test_size: float = 0.2) -> Tuple:
        """Подготовка данных для обучения"""
        # Разделение на признаки и целевую переменную
        feature_cols = [col for col in df.columns if col not in ['timestamp', target_col]]
        X = df[feature_cols].values
        y = df[target_col].values
        
        # Разделение на train/test
        split_idx = int(len(X) * (1 - test_size))
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]
        
        # Разделение train на train/val
        val_size = int(len(X_train) * training_settings.VALIDATION_SPLIT)
        X_val, y_val = X_train[-val_size:], y_train[-val_size:]
        X_train, y_train = X_train[:-val_size], y_train[:-val_size]
        
        return X_train, y_train, X_val, y_val, X_test, y_test, feature_cols
    
    def train_lightgbm(self, X_train, y_train, X_val, y_val) -> Tuple[Any, Dict[str, float]]:
        """Обучение LightGBM модели"""
        trainer = LightGBMTrainer()
        model = trainer.train(X_train, y_train, X_val, y_val)
        
        # Вычисление метрик
        train_pred = trainer.predict(model, X_train)
        val_pred = trainer.predict(model, X_val)
        
        metrics = {
            'train_mae': mean_absolute_error(y_train, train_pred),
            'train_rmse': np.sqrt(mean_squared_error(y_train, train_pred)),
            'train_mape': mean_absolute_percentage_error(y_train, train_pred),
            'val_mae': mean_absolute_error(y_val, val_pred),
            'val_rmse': np.sqrt(mean_squared_error(y_val, val_pred)),
            'val_mape': mean_absolute_percentage_error(y_val, val_pred),
        }
        
        return model, metrics
    
    def train_neural(self, X_train, y_train, X_val, y_val) -> Tuple[Any, Dict[str, float]]:
        """Обучение нейросетевой модели"""
        # Преобразование для LSTM (нужна 3D форма)
        X_train_3d = X_train.reshape(X_train.shape[0], 1, X_train.shape[1])
        X_val_3d = X_val.reshape(X_val.shape[0], 1, X_val.shape[1])
        
        trainer = NeuralTrainer()
        model = trainer.train(X_train_3d, y_train, X_val_3d, y_val)
        
        # Вычисление метрик
        train_pred = trainer.predict(model, X_train_3d)
        val_pred = trainer.predict(model, X_val_3d)
        
        metrics = {
            'train_mae': mean_absolute_error(y_train, train_pred),
            'train_rmse': np.sqrt(mean_squared_error(y_train, train_pred)),
            'train_mape': mean_absolute_percentage_error(y_train, train_pred),
            'val_mae': mean_absolute_error(y_val, val_pred),
            'val_rmse': np.sqrt(mean_squared_error(y_val, val_pred)),
            'val_mape': mean_absolute_percentage_error(y_val, val_pred),
        }
        
        return model, metrics
    
    def save_model_to_s3(self, model_bytes: bytes, model_id: str, version: str) -> str:
        """Сохранение модели в S3"""
        key = f"models/{model_id}/{version}/model.pkl"
        self.s3_client.put_object(
            Bucket=training_settings.MINIO_BUCKET_MODELS,
            Key=key,
            Body=model_bytes,
            ContentType='application/octet-stream'
        )
        return key
    
    async def register_model(self, model_id: str, version: str, artifact_path: str, metrics: Dict[str, float], model_type: str):
        """Регистрация модели в Model Registry"""
        url = f"{training_settings.MODEL_REGISTRY_URL}/models/{model_id}/versions"
        
        version_data = {
            "version": version,
            "artifact_path": artifact_path,
            "training_config": {"model_type": model_type},
            "status": "archived"
        }
        
        response = await self.http_client.post(url, json=version_data)
        version_id = response.json()["id"]
        
        # Сохранение метрик
        for metric_name, metric_value in metrics.items():
            metric_data = {
                "model_version_id": version_id,
                "metric_name": metric_name,
                "metric_value": float(metric_value),
                "dataset_type": "train" if "train" in metric_name else "val"
            }
            await self.http_client.post(
                f"{training_settings.MODEL_REGISTRY_URL}/model-versions/{version_id}/metrics",
                json=metric_data
            )
        
        return version_id
    
    async def train_and_register(self, asset_id: str, model_id: str, model_type: str = "lightgbm"):
        """Полный цикл обучения и регистрации"""
        # Загрузка данных
        end_date = datetime.utcnow()
        start_date = end_date - pd.Timedelta(days=90)
        
        features_df = await self.load_features(asset_id, start_date, end_date)
        
        # Подготовка данных
        X_train, y_train, X_val, y_val, X_test, y_test, feature_cols = self.prepare_data(features_df)
        
        # Обучение
        if model_type == "lightgbm":
            model, metrics = self.train_lightgbm(X_train, y_train, X_val, y_val)
            trainer = LightGBMTrainer()
            model_bytes = trainer.serialize_model(model)
        elif model_type == "neural":
            X_train_3d = X_train.reshape(X_train.shape[0], 1, X_train.shape[1])
            X_val_3d = X_val.reshape(X_val.shape[0], 1, X_val.shape[1])
            model, metrics = self.train_neural(X_train_3d, y_train, X_val_3d, y_val)
            # Сериализация PyTorch модели
            buffer = BytesIO()
            torch.save(model.state_dict(), buffer)
            model_bytes = buffer.getvalue()
        else:
            raise ValueError(f"Unknown model type: {model_type}")
        
        # Сохранение в S3
        version = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        artifact_path = self.save_model_to_s3(model_bytes, model_id, version)
        
        # Регистрация в Model Registry
        version_id = await self.register_model(model_id, version, artifact_path, metrics, model_type)
        
        return {
            "version_id": version_id,
            "version": version,
            "metrics": metrics,
            "artifact_path": artifact_path
        }
    
    async def close(self):
        """Закрытие соединений"""
        await self.http_client.aclose()


"""Предиктор для прогнозирования"""
import numpy as np
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import httpx
import torch
from backend.forecast_service.config import forecast_settings
from backend.forecast_service.model_loader import ModelLoader
from backend.model_training.trainers import LightGBMTrainer, NeuralTrainer


class ForecastPredictor:
    """Класс для выполнения прогнозов"""
    
    def __init__(self):
        self.model_loader = ModelLoader()
        self.http_client = httpx.AsyncClient()
        self.lightgbm_trainer = LightGBMTrainer()
        self.neural_trainer = NeuralTrainer()
    
    async def get_features(self, asset_id: str) -> Optional[Dict[str, Any]]:
        """Получение фичей из Feature Pipeline"""
        url = f"{forecast_settings.FEATURE_PIPELINE_URL}/features/online/{asset_id}"
        response = await self.http_client.get(url, params={"lookback_hours": 24})
        if response.status_code == 200:
            return response.json()
        return None
    
    def prepare_features_array(self, features: Dict[str, Any], feature_order: List[str]) -> np.ndarray:
        """Подготовка массива фичей для модели"""
        feature_values = []
        for feature_name in feature_order:
            value = features.get(feature_name, 0.0)
            if isinstance(value, (int, float)):
                feature_values.append(float(value))
            else:
                feature_values.append(0.0)
        return np.array(feature_values).reshape(1, -1)
    
    async def predict(self, asset_id: str, model_id: str, horizons: List[int] = [1, 7, 30]) -> Dict[str, Any]:
        """Выполнение прогноза"""
        # Получение фичей
        features = await self.get_features(asset_id)
        if not features:
            raise ValueError(f"No features available for asset {asset_id}")
        
        # Загрузка модели
        model = await self.model_loader.get_model(model_id)
        
        # Определение типа модели
        model_version = await self.model_loader.get_prod_model_version(model_id)
        model_type = model_version.get("training_config", {}).get("model_type", "lightgbm")
        
        # Подготовка фичей
        # В реальной реализации порядок фичей должен быть сохранен в метаданных модели
        feature_order = [
            'close_lag_1', 'close_lag_2', 'close_ma_5', 'close_ma_10',
            'close_volatility_5', 'news_count', 'avg_sentiment'
        ]
        X = self.prepare_features_array(features, feature_order)
        
        # Прогнозирование
        if model_type == "lightgbm":
            point_forecast = self.lightgbm_trainer.predict(model, X)[0]
        elif model_type == "neural":
            X_3d = X.reshape(X.shape[0], 1, X.shape[1])
            point_forecast = self.neural_trainer.predict(model, X_3d)[0][0]
        else:
            raise ValueError(f"Unknown model type: {model_type}")
        
        # Вычисление диапазонов (упрощенно - в реальности нужны квантильные модели)
        low_bound = point_forecast * 0.95
        high_bound = point_forecast * 1.05
        
        # Прогнозы для разных горизонтов
        forecasts = {}
        for horizon in horizons:
            # Упрощенная экстраполяция для разных горизонтов
            # В реальности нужны отдельные модели для каждого горизонта
            horizon_multiplier = 1.0 + (horizon - 1) * 0.01  # Простая линейная экстраполяция
            forecasts[f"horizon_{horizon}"] = {
                "point_forecast": float(point_forecast * horizon_multiplier),
                "low_bound": float(low_bound * horizon_multiplier),
                "high_bound": float(high_bound * horizon_multiplier)
            }
        
        return {
            "asset_id": asset_id,
            "model_id": model_id,
            "timestamp_forecasted": datetime.utcnow().isoformat(),
            "forecasts": forecasts
        }
    
    async def close(self):
        """Закрытие соединений"""
        await self.model_loader.close()
        await self.http_client.aclose()


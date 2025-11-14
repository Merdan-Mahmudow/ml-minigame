"""Тренер для LightGBM моделей"""
import lightgbm as lgb
import numpy as np
from typing import Dict, Any, Tuple
import pickle
import io


class LightGBMTrainer:
    """Тренер для LightGBM моделей с квантильной регрессией"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {
            'objective': 'regression',
            'metric': 'rmse',
            'boosting_type': 'gbdt',
            'num_leaves': 31,
            'learning_rate': 0.05,
            'feature_fraction': 0.9,
            'bagging_fraction': 0.8,
            'bagging_freq': 5,
            'verbose': 0
        }
    
    def train(self, X_train, y_train, X_val=None, y_val=None) -> lgb.Booster:
        """Обучение модели"""
        train_data = lgb.Dataset(X_train, label=y_train)
        
        valid_sets = [train_data]
        valid_names = ['train']
        
        if X_val is not None and y_val is not None:
            val_data = lgb.Dataset(X_val, label=y_val, reference=train_data)
            valid_sets.append(val_data)
            valid_names.append('val')
        
        model = lgb.train(
            self.config,
            train_data,
            num_boost_round=100,
            valid_sets=valid_sets,
            valid_names=valid_names,
            callbacks=[lgb.early_stopping(stopping_rounds=10), lgb.log_evaluation(period=10)]
        )
        
        return model
    
    def train_quantile(self, X_train, y_train, quantiles: list = [0.1, 0.5, 0.9], X_val=None, y_val=None) -> Dict[str, lgb.Booster]:
        """Обучение квантильных моделей для диапазонов"""
        models = {}
        
        for quantile in quantiles:
            config = self.config.copy()
            config['objective'] = 'quantile'
            config['alpha'] = quantile
            
            train_data = lgb.Dataset(X_train, label=y_train)
            valid_sets = [train_data]
            valid_names = ['train']
            
            if X_val is not None and y_val is not None:
                val_data = lgb.Dataset(X_val, label=y_val, reference=train_data)
                valid_sets.append(val_data)
                valid_names.append('val')
            
            model = lgb.train(
                config,
                train_data,
                num_boost_round=100,
                valid_sets=valid_sets,
                valid_names=valid_names,
                callbacks=[lgb.early_stopping(stopping_rounds=10), lgb.log_evaluation(period=10)]
            )
            
            models[f'quantile_{quantile}'] = model
        
        return models
    
    def predict(self, model: lgb.Booster, X) -> np.ndarray:
        """Прогнозирование"""
        return model.predict(X)
    
    def save_model(self, model: lgb.Booster, path: str):
        """Сохранение модели"""
        model.save_model(path)
    
    def load_model(self, path: str) -> lgb.Booster:
        """Загрузка модели"""
        return lgb.Booster(model_file=path)
    
    def serialize_model(self, model: lgb.Booster) -> bytes:
        """Сериализация модели в bytes"""
        buffer = io.BytesIO()
        model.save_model(buffer)
        buffer.seek(0)
        return buffer.getvalue()


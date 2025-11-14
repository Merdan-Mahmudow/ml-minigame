"""Вычисление фичей из данных"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any
from datetime import datetime, timedelta


class FeatureEngineer:
    """Класс для вычисления фичей"""
    
    @staticmethod
    def calculate_lags(df: pd.DataFrame, column: str, lags: List[int] = [1, 2, 3, 5, 10]) -> pd.DataFrame:
        """Вычисление лагов"""
        for lag in lags:
            df[f"{column}_lag_{lag}"] = df[column].shift(lag)
        return df
    
    @staticmethod
    def calculate_moving_averages(df: pd.DataFrame, column: str, windows: List[int] = [5, 10, 20, 50]) -> pd.DataFrame:
        """Вычисление скользящих средних"""
        for window in windows:
            df[f"{column}_ma_{window}"] = df[column].rolling(window=window).mean()
        return df
    
    @staticmethod
    def calculate_volatility(df: pd.DataFrame, column: str, windows: List[int] = [5, 10, 20]) -> pd.DataFrame:
        """Вычисление волатильности"""
        for window in windows:
            df[f"{column}_volatility_{window}"] = df[column].rolling(window=window).std()
        return df
    
    @staticmethod
    def calculate_calendar_features(df: pd.DataFrame) -> pd.DataFrame:
        """Вычисление календарных признаков"""
        if 'timestamp' in df.columns:
            df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
            df['day_of_week'] = pd.to_datetime(df['timestamp']).dt.dayofweek
            df['day_of_month'] = pd.to_datetime(df['timestamp']).dt.day
            df['month'] = pd.to_datetime(df['timestamp']).dt.month
            df['is_weekend'] = (pd.to_datetime(df['timestamp']).dt.dayofweek >= 5).astype(int)
        return df
    
    @staticmethod
    def calculate_news_features(news_df: pd.DataFrame) -> Dict[str, float]:
        """Агрегация признаков новостей"""
        if news_df.empty:
            return {
                "news_count": 0,
                "avg_sentiment": 0.0,
                "max_sentiment": 0.0,
                "min_sentiment": 0.0,
                "avg_importance": 0.0,
                "negative_news_count": 0
            }
        
        return {
            "news_count": len(news_df),
            "avg_sentiment": float(news_df['sentiment'].mean()) if 'sentiment' in news_df.columns else 0.0,
            "max_sentiment": float(news_df['sentiment'].max()) if 'sentiment' in news_df.columns else 0.0,
            "min_sentiment": float(news_df['sentiment'].min()) if 'sentiment' in news_df.columns else 0.0,
            "avg_importance": float(news_df['importance'].mean()) if 'importance' in news_df.columns else 0.0,
            "negative_news_count": int((news_df['sentiment'] < 0).sum()) if 'sentiment' in news_df.columns else 0
        }
    
    def compute_features(self, market_data: pd.DataFrame, news_data: pd.DataFrame = None) -> pd.DataFrame:
        """Вычисление всех фичей"""
        df = market_data.copy()
        
        # Лаги цены закрытия
        df = self.calculate_lags(df, 'close', lags=[1, 2, 3, 5, 10, 20])
        
        # Скользящие средние
        df = self.calculate_moving_averages(df, 'close', windows=[5, 10, 20, 50])
        df = self.calculate_moving_averages(df, 'volume', windows=[5, 10, 20])
        
        # Волатильность
        df = self.calculate_volatility(df, 'close', windows=[5, 10, 20])
        
        # Календарные признаки
        df = self.calculate_calendar_features(df)
        
        # Признаки новостей (агрегированные)
        if news_data is not None and not news_data.empty:
            news_features = self.calculate_news_features(news_data)
            for key, value in news_features.items():
                df[key] = value
        else:
            # Заполнение нулями, если новостей нет
            news_features = self.calculate_news_features(pd.DataFrame())
            for key, value in news_features.items():
                df[key] = value
        
        # Дополнительные признаки
        df['price_change'] = df['close'].pct_change()
        df['high_low_ratio'] = df['high'] / df['low']
        df['volume_price_trend'] = df['volume'] * df['close']
        
        return df


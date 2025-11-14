"""Вычисление метрик качества моделей"""
import numpy as np
from typing import List, Dict, Any
from datetime import datetime
from decimal import Decimal


class MetricsCalculator:
    """Калькулятор метрик качества"""
    
    @staticmethod
    def calculate_mae(actual: List[float], predicted: List[float]) -> float:
        """Mean Absolute Error"""
        return float(np.mean(np.abs(np.array(actual) - np.array(predicted))))
    
    @staticmethod
    def calculate_rmse(actual: List[float], predicted: List[float]) -> float:
        """Root Mean Squared Error"""
        return float(np.sqrt(np.mean((np.array(actual) - np.array(predicted)) ** 2)))
    
    @staticmethod
    def calculate_mape(actual: List[float], predicted: List[float]) -> float:
        """Mean Absolute Percentage Error"""
        actual_arr = np.array(actual)
        predicted_arr = np.array(predicted)
        # Избегаем деления на ноль
        mask = actual_arr != 0
        if not mask.any():
            return 0.0
        return float(np.mean(np.abs((actual_arr[mask] - predicted_arr[mask]) / actual_arr[mask]) * 100))
    
    @staticmethod
    def calculate_coverage(actual: List[float], low: List[float], high: List[float]) -> float:
        """Coverage - процент фактических значений в интервале прогноза"""
        actual_arr = np.array(actual)
        low_arr = np.array(low)
        high_arr = np.array(high)
        in_range = (actual_arr >= low_arr) & (actual_arr <= high_arr)
        return float(np.mean(in_range) * 100)
    
    def calculate_all_metrics(self, forecasts: List[Dict[str, Any]]) -> Dict[str, float]:
        """Вычисление всех метрик"""
        actual = [float(f.get("actual_value", 0)) for f in forecasts if f.get("actual_value")]
        predicted = [float(f.get("point_forecast", 0)) for f in forecasts if f.get("point_forecast")]
        low = [float(f.get("low_bound", 0)) for f in forecasts if f.get("low_bound")]
        high = [float(f.get("high_bound", 0)) for f in forecasts if f.get("high_bound")]
        
        if not actual or not predicted or len(actual) != len(predicted):
            return {}
        
        metrics = {
            "mae": self.calculate_mae(actual, predicted),
            "rmse": self.calculate_rmse(actual, predicted),
            "mape": self.calculate_mape(actual, predicted)
        }
        
        if low and high and len(low) == len(actual):
            metrics["coverage"] = self.calculate_coverage(actual, low, high)
        
        return metrics


"""Менеджер алертов"""
import httpx
from typing import Dict, Any
from backend.monitoring_service.config import monitoring_settings


class AlertManager:
    """Менеджер для отправки алертов"""
    
    def __init__(self):
        self.http_client = httpx.AsyncClient()
    
    async def send_alert(self, message: str, severity: str = "warning"):
        """Отправка алерта"""
        alerts_sent = []
        
        # Slack
        if monitoring_settings.ALERT_SLACK_WEBHOOK:
            try:
                await self.http_client.post(
                    monitoring_settings.ALERT_SLACK_WEBHOOK,
                    json={"text": f"[{severity.upper()}] {message}"}
                )
                alerts_sent.append("slack")
            except Exception as e:
                print(f"Failed to send Slack alert: {e}")
        
        # Telegram
        if monitoring_settings.ALERT_TELEGRAM_BOT_TOKEN and monitoring_settings.ALERT_TELEGRAM_CHAT_ID:
            try:
                url = f"https://api.telegram.org/bot{monitoring_settings.ALERT_TELEGRAM_BOT_TOKEN}/sendMessage"
                await self.http_client.post(
                    url,
                    json={
                        "chat_id": monitoring_settings.ALERT_TELEGRAM_CHAT_ID,
                        "text": f"[{severity.upper()}] {message}"
                    }
                )
                alerts_sent.append("telegram")
            except Exception as e:
                print(f"Failed to send Telegram alert: {e}")
        
        # Email (упрощенно - в реальности нужен SMTP клиент)
        if monitoring_settings.ALERT_EMAIL:
            print(f"Email alert to {monitoring_settings.ALERT_EMAIL}: {message}")
            alerts_sent.append("email")
        
        return alerts_sent
    
    async def check_metrics_thresholds(self, metrics: Dict[str, float]):
        """Проверка метрик на превышение порогов"""
        alerts = []
        
        if metrics.get("mae", 0) > monitoring_settings.MAE_THRESHOLD:
            alerts.append(f"MAE ({metrics['mae']:.2f}) exceeds threshold ({monitoring_settings.MAE_THRESHOLD})")
        
        if metrics.get("mape", 0) > monitoring_settings.MAPE_THRESHOLD:
            alerts.append(f"MAPE ({metrics['mape']:.2f}%) exceeds threshold ({monitoring_settings.MAPE_THRESHOLD}%)")
        
        if metrics.get("rmse", 0) > monitoring_settings.RMSE_THRESHOLD:
            alerts.append(f"RMSE ({metrics['rmse']:.2f}) exceeds threshold ({monitoring_settings.RMSE_THRESHOLD})")
        
        if alerts:
            message = "Model quality alerts:\n" + "\n".join(alerts)
            await self.send_alert(message, severity="error")
        
        return alerts
    
    async def close(self):
        """Закрытие соединений"""
        await self.http_client.aclose()


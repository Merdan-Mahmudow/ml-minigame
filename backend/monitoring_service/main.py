"""Monitoring & Quality Service - мониторинг качества моделей"""
from fastapi import FastAPI, HTTPException, Query
from backend.shared.models import HealthResponse
from backend.monitoring_service.metrics_calculator import MetricsCalculator
from backend.monitoring_service.alert_manager import AlertManager
from backend.monitoring_service.config import monitoring_settings
from typing import Optional
from datetime import datetime, timedelta
import httpx
import time

app = FastAPI(
    title="Monitoring & Quality Service",
    description="Сервис мониторинга качества моделей",
    version="1.0.0"
)

metrics_calculator = MetricsCalculator()
alert_manager = AlertManager()
http_client = httpx.AsyncClient()


@app.on_event("shutdown")
async def shutdown():
    await alert_manager.close()
    await http_client.aclose()


@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check"""
    return HealthResponse(
        status="healthy",
        service="monitoring-service",
        timestamp=time.time()
    )


@app.post("/metrics/calculate/{asset_id}")
async def calculate_metrics(
    asset_id: str,
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None)
):
    """Вычисление метрик качества для актива"""
    try:
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()
        
        # Получение прогнозов с фактическими значениями
        response = await http_client.get(
            f"{monitoring_settings.FORECAST_STORAGE_URL}/forecasts",
            params={
                "asset_id": asset_id,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            }
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=404, detail="No forecasts found")
        
        forecasts = response.json()
        
        # Получение метрик для каждого прогноза
        forecasts_with_metrics = []
        for forecast in forecasts:
            forecast_id = forecast.get("id")
            if forecast_id:
                metrics_response = await http_client.get(
                    f"{monitoring_settings.FORECAST_STORAGE_URL}/forecasts/{forecast_id}/metrics"
                )
                if metrics_response.status_code == 200:
                    forecast_metrics = metrics_response.json()
                    if forecast_metrics:
                        forecast["actual_value"] = forecast_metrics[0].get("actual_value")
                        forecast["error"] = forecast_metrics[0].get("error")
            forecasts_with_metrics.append(forecast)
        
        # Вычисление метрик
        metrics = metrics_calculator.calculate_all_metrics(forecasts_with_metrics)
        
        # Проверка порогов и отправка алертов
        alerts = await alert_manager.check_metrics_thresholds(metrics)
        
        return {
            "asset_id": asset_id,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "metrics": metrics,
            "alerts": alerts,
            "forecasts_count": len(forecasts_with_metrics)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/metrics/{asset_id}/summary")
async def get_metrics_summary(asset_id: str):
    """Получение сводки метрик"""
    try:
        # Получение последних прогнозов
        response = await http_client.get(
            f"{monitoring_settings.FORECAST_STORAGE_URL}/forecasts",
            params={"asset_id": asset_id, "limit": 100}
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=404, detail="No forecasts found")
        
        forecasts = response.json()
        
        # Вычисление метрик
        metrics = metrics_calculator.calculate_all_metrics(forecasts)
        
        return {
            "asset_id": asset_id,
            "metrics": metrics,
            "last_updated": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/alerts/test")
async def test_alert(message: str = "Test alert"):
    """Тестовая отправка алерта"""
    alerts_sent = await alert_manager.send_alert(message, severity="info")
    return {"status": "sent", "channels": alerts_sent}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8009, reload=True)


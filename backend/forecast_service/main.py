"""Forecast Service - онлайновое прогнозирование"""
from fastapi import FastAPI, HTTPException, Query
from backend.shared.models import HealthResponse
from backend.forecast_service.predictor import ForecastPredictor
from backend.forecast_service.config import forecast_settings
from typing import List, Optional
from uuid import UUID
import time
import httpx

app = FastAPI(
    title="Forecast Service",
    description="Сервис онлайнового прогнозирования",
    version="1.0.0"
)

predictor = ForecastPredictor()
http_client = httpx.AsyncClient()


@app.on_event("shutdown")
async def shutdown():
    await predictor.close()
    await http_client.aclose()


@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check"""
    return HealthResponse(
        status="healthy",
        service="forecast-service",
        timestamp=time.time()
    )


@app.get("/forecast/{asset_id}")
async def get_forecast(
    asset_id: str,
    model_id: Optional[str] = Query(None),
    horizons: Optional[str] = Query("1,7,30"),  # дни
    save: bool = Query(True)
):
    """Получение прогноза для актива"""
    try:
        # Парсинг горизонтов
        horizon_list = [int(h.strip()) for h in horizons.split(",")]
        
        # Если model_id не указан, получаем первую доступную модель
        if not model_id:
            # В реальной реализации здесь будет логика выбора модели
            # Для примера используем фиксированный ID
            model_id = "00000000-0000-0000-0000-000000000001"
        
        # Выполнение прогноза
        forecast_result = await predictor.predict(asset_id, model_id, horizon_list)
        
        # Сохранение в Forecast Storage
        if save:
            for horizon_key, forecast_data in forecast_result["forecasts"].items():
                horizon = int(horizon_key.split("_")[1])
                forecast_payload = {
                    "asset_id": asset_id,
                    "model_version_id": model_id,
                    "timestamp_forecasted": forecast_result["timestamp_forecasted"],
                    "horizon": horizon,
                    "point_forecast": forecast_data["point_forecast"],
                    "low_bound": forecast_data["low_bound"],
                    "high_bound": forecast_data["high_bound"]
                }
                
                try:
                    await http_client.post(
                        f"{forecast_settings.FORECAST_STORAGE_URL}/forecasts",
                        json=forecast_payload
                    )
                except Exception as e:
                    print(f"Failed to save forecast: {e}")
        
        return forecast_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/forecast/{asset_id}/latest")
async def get_latest_forecast(
    asset_id: str,
    horizon: int = Query(1, ge=1)
):
    """Получение последнего сохраненного прогноза"""
    try:
        response = await http_client.get(
            f"{forecast_settings.FORECAST_STORAGE_URL}/forecasts/asset/{asset_id}/latest",
            params={"horizon": horizon}
        )
        if response.status_code == 200:
            return response.json()
        raise HTTPException(status_code=404, detail="No forecast found")
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Service unavailable: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=True)


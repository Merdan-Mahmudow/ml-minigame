"""Forecast Storage Service - хранение готовых прогнозов"""
from fastapi import FastAPI, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timedelta
from backend.forecast_storage.database import get_db, Base, engine
from backend.forecast_storage import models, schemas
from backend.shared.models import HealthResponse
import time

app = FastAPI(
    title="Forecast Storage Service",
    description="Сервис хранения готовых прогнозов",
    version="1.0.0"
)

# Создание таблиц при старте
@app.on_event("startup")
async def startup():
    Base.metadata.create_all(bind=engine)


@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check"""
    return HealthResponse(
        status="healthy",
        service="forecast-storage",
        timestamp=time.time()
    )


@app.post("/forecasts", response_model=schemas.ForecastResponse, status_code=status.HTTP_201_CREATED)
async def create_forecast(forecast: schemas.ForecastCreate, db: Session = Depends(get_db)):
    """Создание нового прогноза"""
    db_forecast = models.Forecast(**forecast.dict())
    db.add(db_forecast)
    db.commit()
    db.refresh(db_forecast)
    return db_forecast


@app.post("/forecasts/batch", status_code=status.HTTP_201_CREATED)
async def create_forecasts_batch(
    forecasts: List[schemas.ForecastCreate],
    db: Session = Depends(get_db)
):
    """Создание нескольких прогнозов"""
    db_forecasts = [models.Forecast(**f.dict()) for f in forecasts]
    db.add_all(db_forecasts)
    db.commit()
    return {"created": len(db_forecasts)}


@app.get("/forecasts", response_model=List[schemas.ForecastResponse])
async def get_forecasts(
    asset_id: Optional[UUID] = Query(None),
    model_version_id: Optional[UUID] = Query(None),
    horizon: Optional[int] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Получение списка прогнозов с фильтрацией"""
    query = db.query(models.Forecast)
    
    if asset_id:
        query = query.filter(models.Forecast.asset_id == asset_id)
    if model_version_id:
        query = query.filter(models.Forecast.model_version_id == model_version_id)
    if horizon:
        query = query.filter(models.Forecast.horizon == horizon)
    if start_date:
        query = query.filter(models.Forecast.timestamp_forecasted >= start_date)
    if end_date:
        query = query.filter(models.Forecast.timestamp_forecasted <= end_date)
    
    forecasts = query.order_by(models.Forecast.created_at.desc()).offset(skip).limit(limit).all()
    return forecasts


@app.get("/forecasts/{forecast_id}", response_model=schemas.ForecastResponse)
async def get_forecast(forecast_id: UUID, db: Session = Depends(get_db)):
    """Получение прогноза по ID"""
    forecast = db.query(models.Forecast).filter(models.Forecast.id == forecast_id).first()
    if not forecast:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Forecast not found"
        )
    return forecast


@app.get("/forecasts/asset/{asset_id}/latest", response_model=schemas.ForecastResponse)
async def get_latest_forecast(
    asset_id: UUID,
    horizon: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """Получение последнего прогноза для актива"""
    query = db.query(models.Forecast).filter(models.Forecast.asset_id == asset_id)
    if horizon:
        query = query.filter(models.Forecast.horizon == horizon)
    
    forecast = query.order_by(models.Forecast.created_at.desc()).first()
    if not forecast:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No forecast found for this asset"
        )
    return forecast


@app.post("/forecasts/{forecast_id}/metrics", response_model=schemas.ForecastMetricResponse, status_code=status.HTTP_201_CREATED)
async def create_forecast_metric(
    forecast_id: UUID,
    metric: schemas.ForecastMetricCreate,
    db: Session = Depends(get_db)
):
    """Создание метрики для прогноза"""
    # Проверка существования прогноза
    forecast = db.query(models.Forecast).filter(models.Forecast.id == forecast_id).first()
    if not forecast:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Forecast not found"
        )
    
    db_metric = models.ForecastMetric(forecast_id=forecast_id, **metric.dict(exclude={'forecast_id'}))
    db.add(db_metric)
    db.commit()
    db.refresh(db_metric)
    return db_metric


@app.get("/forecasts/{forecast_id}/metrics", response_model=List[schemas.ForecastMetricResponse])
async def get_forecast_metrics(forecast_id: UUID, db: Session = Depends(get_db)):
    """Получение метрик для прогноза"""
    metrics = db.query(models.ForecastMetric).filter(
        models.ForecastMetric.forecast_id == forecast_id
    ).all()
    return metrics


@app.delete("/forecasts/{forecast_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_forecast(forecast_id: UUID, db: Session = Depends(get_db)):
    """Удаление прогноза"""
    forecast = db.query(models.Forecast).filter(models.Forecast.id == forecast_id).first()
    if not forecast:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Forecast not found"
        )
    db.delete(forecast)
    db.commit()
    return None


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8008, reload=True)


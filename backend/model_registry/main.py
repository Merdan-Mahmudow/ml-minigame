"""Model Registry Service - управление версиями моделей"""
from fastapi import FastAPI, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from backend.model_registry.database import get_db, Base, engine
from backend.model_registry import models, schemas
from backend.shared.models import HealthResponse
import time

app = FastAPI(
    title="Model Registry Service",
    description="Сервис управления версиями моделей",
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
        service="model-registry",
        timestamp=time.time()
    )


@app.post("/models", response_model=schemas.ModelResponse, status_code=status.HTTP_201_CREATED)
async def create_model(model: schemas.ModelCreate, db: Session = Depends(get_db)):
    """Создание новой модели"""
    db_model = models.Model(**model.dict())
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    return db_model


@app.get("/models", response_model=List[schemas.ModelResponse])
async def get_models(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    model_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Получение списка моделей"""
    query = db.query(models.Model)
    if model_type:
        query = query.filter(models.Model.model_type == model_type)
    models_list = query.offset(skip).limit(limit).all()
    return models_list


@app.get("/models/{model_id}", response_model=schemas.ModelResponse)
async def get_model(model_id: UUID, db: Session = Depends(get_db)):
    """Получение модели по ID"""
    model = db.query(models.Model).filter(models.Model.id == model_id).first()
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found"
        )
    return model


@app.post("/models/{model_id}/versions", response_model=schemas.ModelVersionResponse, status_code=status.HTTP_201_CREATED)
async def create_model_version(
    model_id: UUID,
    version: schemas.ModelVersionBase,
    db: Session = Depends(get_db)
):
    """Создание новой версии модели"""
    # Проверка существования модели
    model = db.query(models.Model).filter(models.Model.id == model_id).first()
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found"
        )
    
    # Проверка на существующую версию
    existing = db.query(models.ModelVersion).filter(
        models.ModelVersion.model_id == model_id,
        models.ModelVersion.version == version.version
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Model version already exists"
        )
    
    db_version = models.ModelVersion(model_id=model_id, **version.dict())
    db.add(db_version)
    db.commit()
    db.refresh(db_version)
    return db_version


@app.get("/models/{model_id}/versions", response_model=List[schemas.ModelVersionResponse])
async def get_model_versions(
    model_id: UUID,
    status_filter: Optional[str] = Query(None, alias="status"),
    db: Session = Depends(get_db)
):
    """Получение версий модели"""
    query = db.query(models.ModelVersion).filter(models.ModelVersion.model_id == model_id)
    if status_filter:
        query = query.filter(models.ModelVersion.status == status_filter)
    versions = query.order_by(models.ModelVersion.trained_at.desc()).all()
    return versions


@app.get("/models/{model_id}/versions/{version_id}", response_model=schemas.ModelVersionWithMetrics)
async def get_model_version(
    model_id: UUID,
    version_id: UUID,
    db: Session = Depends(get_db)
):
    """Получение версии модели с метриками"""
    version = db.query(models.ModelVersion).filter(
        models.ModelVersion.id == version_id,
        models.ModelVersion.model_id == model_id
    ).first()
    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model version not found"
        )
    
    metrics = db.query(models.ModelMetric).filter(
        models.ModelMetric.model_version_id == version_id
    ).all()
    
    response = schemas.ModelVersionWithMetrics.from_orm(version)
    response.metrics = [schemas.ModelMetricResponse.from_orm(m) for m in metrics]
    return response


@app.patch("/models/{model_id}/versions/{version_id}/status")
async def update_model_version_status(
    model_id: UUID,
    version_id: UUID,
    new_status: str,
    db: Session = Depends(get_db)
):
    """Обновление статуса версии модели"""
    version = db.query(models.ModelVersion).filter(
        models.ModelVersion.id == version_id,
        models.ModelVersion.model_id == model_id
    ).first()
    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model version not found"
        )
    
    if new_status not in ["prod", "canary", "archived"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid status. Must be: prod, canary, or archived"
        )
    
    # Если устанавливаем prod, архивируем другие prod версии этой модели
    if new_status == "prod":
        db.query(models.ModelVersion).filter(
            models.ModelVersion.model_id == model_id,
            models.ModelVersion.status == "prod",
            models.ModelVersion.id != version_id
        ).update({"status": "archived"})
    
    version.status = new_status
    db.commit()
    db.refresh(version)
    return version


@app.get("/models/{model_id}/versions/prod", response_model=schemas.ModelVersionResponse)
async def get_prod_version(model_id: UUID, db: Session = Depends(get_db)):
    """Получение продакшн-версии модели"""
    version = db.query(models.ModelVersion).filter(
        models.ModelVersion.model_id == model_id,
        models.ModelVersion.status == "prod"
    ).first()
    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No production version found for this model"
        )
    return version


@app.post("/model-versions/{version_id}/metrics", response_model=schemas.ModelMetricResponse, status_code=status.HTTP_201_CREATED)
async def create_model_metric(
    version_id: UUID,
    metric: schemas.ModelMetricCreate,
    db: Session = Depends(get_db)
):
    """Создание метрики для версии модели"""
    # Проверка существования версии
    version = db.query(models.ModelVersion).filter(models.ModelVersion.id == version_id).first()
    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model version not found"
        )
    
    db_metric = models.ModelMetric(model_version_id=version_id, **metric.dict(exclude={'model_version_id'}))
    db.add(db_metric)
    db.commit()
    db.refresh(db_metric)
    return db_metric


@app.get("/model-versions/{version_id}/metrics", response_model=List[schemas.ModelMetricResponse])
async def get_model_metrics(version_id: UUID, db: Session = Depends(get_db)):
    """Получение метрик версии модели"""
    metrics = db.query(models.ModelMetric).filter(
        models.ModelMetric.model_version_id == version_id
    ).all()
    return metrics


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8007, reload=True)


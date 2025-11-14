"""Asset Service - управление активами"""
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from backend.asset_service.database import get_db, Base, engine
from backend.asset_service import models, schemas
from backend.shared.models import HealthResponse
import time

app = FastAPI(
    title="Asset Service",
    description="Сервис управления активами",
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
        service="asset-service",
        timestamp=time.time()
    )


@app.get("/assets", response_model=List[schemas.AssetResponse])
async def get_assets(
    skip: int = 0,
    limit: int = 100,
    asset_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Получение списка активов"""
    query = db.query(models.Asset)
    if asset_type:
        query = query.filter(models.Asset.asset_type == asset_type)
    assets = query.offset(skip).limit(limit).all()
    return assets


@app.get("/assets/{asset_id}", response_model=schemas.AssetResponse)
async def get_asset(asset_id: UUID, db: Session = Depends(get_db)):
    """Получение актива по ID"""
    asset = db.query(models.Asset).filter(models.Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found"
        )
    return asset


@app.post("/assets", response_model=schemas.AssetResponse, status_code=status.HTTP_201_CREATED)
async def create_asset(asset: schemas.AssetCreate, db: Session = Depends(get_db)):
    """Создание нового актива"""
    # Проверка на существующий ticker
    existing = db.query(models.Asset).filter(models.Asset.ticker == asset.ticker).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Asset with this ticker already exists"
        )
    
    db_asset = models.Asset(**asset.dict())
    db.add(db_asset)
    db.commit()
    db.refresh(db_asset)
    return db_asset


@app.patch("/assets/{asset_id}", response_model=schemas.AssetResponse)
async def update_asset(
    asset_id: UUID,
    asset_update: schemas.AssetUpdate,
    db: Session = Depends(get_db)
):
    """Обновление актива"""
    db_asset = db.query(models.Asset).filter(models.Asset.id == asset_id).first()
    if not db_asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found"
        )
    
    update_data = asset_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_asset, field, value)
    
    db.commit()
    db.refresh(db_asset)
    return db_asset


@app.delete("/assets/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_asset(asset_id: UUID, db: Session = Depends(get_db)):
    """Удаление актива"""
    db_asset = db.query(models.Asset).filter(models.Asset.id == asset_id).first()
    if not db_asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found"
        )
    db.delete(db_asset)
    db.commit()
    return None


@app.get("/assets/{asset_id}/config", response_model=schemas.AssetConfigResponse)
async def get_asset_config(asset_id: UUID, db: Session = Depends(get_db)):
    """Получение конфигурации актива"""
    config = db.query(models.AssetConfig).filter(
        models.AssetConfig.asset_id == asset_id
    ).first()
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset config not found"
        )
    return config


@app.post("/assets/{asset_id}/config", response_model=schemas.AssetConfigResponse)
async def create_asset_config(
    asset_id: UUID,
    config: schemas.AssetConfigBase,
    db: Session = Depends(get_db)
):
    """Создание конфигурации актива"""
    # Проверка существования актива
    asset = db.query(models.Asset).filter(models.Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found"
        )
    
    # Проверка на существующую конфигурацию
    existing = db.query(models.AssetConfig).filter(
        models.AssetConfig.asset_id == asset_id
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Asset config already exists"
        )
    
    db_config = models.AssetConfig(asset_id=asset_id, **config.dict())
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    return db_config


@app.get("/data-sources", response_model=List[schemas.DataSourceResponse])
async def get_data_sources(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Получение списка источников данных"""
    sources = db.query(models.DataSource).offset(skip).limit(limit).all()
    return sources


@app.post("/data-sources", response_model=schemas.DataSourceResponse, status_code=status.HTTP_201_CREATED)
async def create_data_source(source: schemas.DataSourceCreate, db: Session = Depends(get_db)):
    """Создание источника данных"""
    existing = db.query(models.DataSource).filter(
        models.DataSource.name == source.name
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Data source with this name already exists"
        )
    
    db_source = models.DataSource(**source.dict())
    db.add(db_source)
    db.commit()
    db.refresh(db_source)
    return db_source


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)


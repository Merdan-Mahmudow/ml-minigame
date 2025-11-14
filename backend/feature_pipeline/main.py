"""Feature Pipeline Service - вычисление фичей"""
from fastapi import FastAPI, HTTPException, Query
from backend.shared.models import HealthResponse
from backend.feature_pipeline.batch_processor import BatchFeatureProcessor
from backend.feature_pipeline.online_processor import OnlineFeatureProcessor
from datetime import datetime, timedelta
from typing import Optional
import time

app = FastAPI(
    title="Feature Pipeline Service",
    description="Сервис вычисления фичей для моделей",
    version="1.0.0"
)

batch_processor = BatchFeatureProcessor()
online_processor = OnlineFeatureProcessor()


@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check"""
    return HealthResponse(
        status="healthy",
        service="feature-pipeline",
        timestamp=time.time()
    )


@app.post("/features/batch/{asset_id}")
async def compute_batch_features(
    asset_id: str,
    start_time: Optional[datetime] = Query(None),
    end_time: Optional[datetime] = Query(None)
):
    """Batch-вычисление фичей для актива"""
    if not start_time:
        start_time = datetime.utcnow() - timedelta(days=30)
    if not end_time:
        end_time = datetime.utcnow()
    
    try:
        batch_processor.process_asset(asset_id, start_time, end_time)
        return {"status": "completed", "asset_id": asset_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/features/online/{asset_id}")
async def compute_online_features(
    asset_id: str,
    lookback_hours: int = Query(24, ge=1, le=168)
):
    """Online-вычисление фичей для актива"""
    try:
        features = online_processor.compute_features(asset_id, lookback_hours)
        if not features:
            raise HTTPException(status_code=404, detail="No features available")
        return features
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8005, reload=True)


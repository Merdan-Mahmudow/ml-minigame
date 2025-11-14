"""Model Training Service - обучение моделей"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from backend.shared.models import HealthResponse
from backend.model_training.training_pipeline import TrainingPipeline
from uuid import UUID
import time
import asyncio

app = FastAPI(
    title="Model Training Service",
    description="Сервис обучения моделей",
    version="1.0.0"
)

training_pipeline = TrainingPipeline()


@app.on_event("shutdown")
async def shutdown():
    await training_pipeline.close()


@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check"""
    return HealthResponse(
        status="healthy",
        service="model-training",
        timestamp=time.time()
    )


async def train_model_task(asset_id: str, model_id: str, model_type: str):
    """Фоновая задача обучения модели"""
    try:
        result = await training_pipeline.train_and_register(asset_id, model_id, model_type)
        print(f"Training completed: {result}")
    except Exception as e:
        print(f"Training failed: {e}")


@app.post("/train")
async def train_model(
    asset_id: str,
    model_id: str,
    model_type: str = "lightgbm",
    background_tasks: BackgroundTasks = None
):
    """Запуск обучения модели"""
    if model_type not in ["lightgbm", "neural"]:
        raise HTTPException(status_code=400, detail="model_type must be 'lightgbm' or 'neural'")
    
    # Запуск в фоне
    if background_tasks:
        background_tasks.add_task(train_model_task, asset_id, model_id, model_type)
        return {"status": "training_started", "asset_id": asset_id, "model_id": model_id}
    else:
        # Синхронное выполнение (для тестирования)
        result = await training_pipeline.train_and_register(asset_id, model_id, model_type)
        return result


@app.get("/train/status/{job_id}")
async def get_training_status(job_id: str):
    """Получение статуса обучения (заглушка)"""
    # В реальной реализации здесь будет проверка статуса через очередь задач
    return {"status": "completed", "job_id": job_id}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8006, reload=True)


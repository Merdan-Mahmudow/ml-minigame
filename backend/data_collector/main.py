"""Data Collector Service - сбор рыночных данных"""
from fastapi import FastAPI
from backend.shared.models import HealthResponse
import asyncio
import time
from backend.data_collector.worker import DataCollectorWorker
from backend.data_collector.scheduler import DataCollectionScheduler

app = FastAPI(
    title="Data Collector Service",
    description="Сервис сбора рыночных данных",
    version="1.0.0"
)

worker = None
scheduler = None


@app.on_event("startup")
async def startup():
    """Запуск worker и scheduler"""
    global worker, scheduler
    
    # Запуск scheduler
    scheduler = DataCollectionScheduler()
    scheduler.start()
    
    # Запуск worker в фоне
    worker = DataCollectorWorker()
    asyncio.create_task(worker.run())


@app.on_event("shutdown")
async def shutdown():
    """Остановка worker и scheduler"""
    global worker, scheduler
    
    if scheduler:
        scheduler.stop()
        await scheduler.close()
    
    if worker:
        await worker.close()


@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check"""
    return HealthResponse(
        status="healthy",
        service="data-collector",
        timestamp=time.time()
    )


@app.post("/trigger-collection")
async def trigger_collection():
    """Ручной запуск сбора данных"""
    if scheduler:
        await scheduler.create_collection_tasks()
        return {"status": "triggered"}
    return {"status": "scheduler not available"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8003, reload=True)


"""News & Text Collector Service - сбор новостей"""
from fastapi import FastAPI
from backend.shared.models import HealthResponse
import asyncio
import time
from backend.news_collector.worker import NewsCollectorWorker
from backend.news_collector.scheduler import NewsCollectionScheduler

app = FastAPI(
    title="News Collector Service",
    description="Сервис сбора новостей и текстов",
    version="1.0.0"
)

worker = None
scheduler = None


@app.on_event("startup")
async def startup():
    """Запуск worker и scheduler"""
    global worker, scheduler
    
    # Запуск scheduler
    scheduler = NewsCollectionScheduler()
    scheduler.start()
    
    # Запуск worker в фоне
    worker = NewsCollectorWorker()
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
        service="news-collector",
        timestamp=time.time()
    )


@app.post("/trigger-collection")
async def trigger_collection():
    """Ручной запуск сбора новостей"""
    if scheduler:
        await scheduler.create_collection_tasks()
        return {"status": "triggered"}
    return {"status": "scheduler not available"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8004, reload=True)


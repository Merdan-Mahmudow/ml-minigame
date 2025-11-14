"""API Gateway - единая точка входа для всех клиентов"""
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import httpx
from typing import Optional
import time
from backend.shared.config import settings
from backend.shared.models import HealthResponse, ErrorResponse
from backend.shared.auth import get_current_user, create_access_token
from datetime import timedelta

app = FastAPI(
    title="Forecast API Gateway",
    description="Единая точка входа для системы прогнозирования",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Клиент для проксирования запросов
http_client = httpx.AsyncClient(timeout=30.0)


@app.on_event("shutdown")
async def shutdown():
    await http_client.aclose()


@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check"""
    return HealthResponse(
        status="healthy",
        service="api-gateway",
        timestamp=time.time()
    )


@app.post("/auth/login")
async def login(username: str, password: str):
    """Простая авторизация (в продакшене использовать реальную БД)"""
    # TODO: Проверка в БД пользователей
    if username and password:  # Упрощенная проверка
        access_token = create_access_token(
            data={"sub": username},
            expires_delta=timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        return {"access_token": access_token, "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Invalid credentials")


@app.get("/api/assets")
async def get_assets(
    request: Request,
    current_user: str = Depends(get_current_user)
):
    """Проксирование запроса к Asset Service"""
    try:
        url = f"{settings.ASSET_SERVICE_URL}/assets"
        params = dict(request.query_params)
        response = await http_client.get(url, params=params)
        return JSONResponse(
            content=response.json(),
            status_code=response.status_code
        )
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Service unavailable: {str(e)}")


@app.post("/api/assets")
async def create_asset(
    request: Request,
    current_user: str = Depends(get_current_user)
):
    """Создание актива"""
    try:
        body = await request.json()
        url = f"{settings.ASSET_SERVICE_URL}/assets"
        response = await http_client.post(url, json=body)
        return JSONResponse(
            content=response.json(),
            status_code=response.status_code
        )
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Service unavailable: {str(e)}")


@app.get("/api/assets/{asset_id}")
async def get_asset(
    asset_id: str,
    current_user: str = Depends(get_current_user)
):
    """Получение актива по ID"""
    try:
        url = f"{settings.ASSET_SERVICE_URL}/assets/{asset_id}"
        response = await http_client.get(url)
        return JSONResponse(
            content=response.json(),
            status_code=response.status_code
        )
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Service unavailable: {str(e)}")


@app.patch("/api/assets/{asset_id}")
async def update_asset(
    asset_id: str,
    request: Request,
    current_user: str = Depends(get_current_user)
):
    """Обновление актива"""
    try:
        body = await request.json()
        url = f"{settings.ASSET_SERVICE_URL}/assets/{asset_id}"
        response = await http_client.patch(url, json=body)
        return JSONResponse(
            content=response.json(),
            status_code=response.status_code
        )
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Service unavailable: {str(e)}")


@app.get("/api/forecast/{asset_id}")
async def get_forecast(
    asset_id: str,
    horizon: Optional[int] = None,
    current_user: str = Depends(get_current_user)
):
    """Получение прогноза для актива"""
    try:
        url = f"{settings.FORECAST_SERVICE_URL}/forecast/{asset_id}"
        params = {"horizon": horizon} if horizon else {}
        response = await http_client.get(url, params=params)
        return JSONResponse(
            content=response.json(),
            status_code=response.status_code
        )
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Service unavailable: {str(e)}")


@app.get("/api/forecasts/history")
async def get_forecast_history(
    request: Request,
    current_user: str = Depends(get_current_user)
):
    """Получение истории прогнозов"""
    try:
        url = f"{settings.FORECAST_STORAGE_URL}/forecasts"
        params = dict(request.query_params)
        response = await http_client.get(url, params=params)
        return JSONResponse(
            content=response.json(),
            status_code=response.status_code
        )
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Service unavailable: {str(e)}")


@app.get("/api/models")
async def get_models(
    request: Request,
    current_user: str = Depends(get_current_user)
):
    """Получение списка моделей"""
    try:
        url = f"{settings.MODEL_REGISTRY_URL}/models"
        params = dict(request.query_params)
        response = await http_client.get(url, params=params)
        return JSONResponse(
            content=response.json(),
            status_code=response.status_code
        )
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Service unavailable: {str(e)}")


@app.get("/api/admin/{path:path}")
async def admin_proxy(
    path: str,
    request: Request,
    current_user: str = Depends(get_current_user)
):
    """Проксирование админских запросов"""
    try:
        method = request.method
        url = f"{settings.ADMIN_SERVICE_URL}/{path}"
        params = dict(request.query_params)
        
        if method == "GET":
            response = await http_client.get(url, params=params)
        elif method == "POST":
            body = await request.json()
            response = await http_client.post(url, json=body, params=params)
        elif method == "PATCH":
            body = await request.json()
            response = await http_client.patch(url, json=body, params=params)
        elif method == "DELETE":
            response = await http_client.delete(url, params=params)
        else:
            raise HTTPException(status_code=405, detail="Method not allowed")
        
        return JSONResponse(
            content=response.json(),
            status_code=response.status_code
        )
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Service unavailable: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.API_GATEWAY_HOST,
        port=settings.API_GATEWAY_PORT,
        reload=True
    )


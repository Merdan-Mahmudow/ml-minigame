# Система прогнозирования

Полнофункциональная система прогнозирования с микросервисной архитектурой.

## Архитектура

Система состоит из 12 микросервисов:

1. **API Gateway** - единая точка входа
2. **Asset Service** - управление активами
3. **Data Collector** - сбор рыночных данных
4. **News Collector** - сбор новостей
5. **Feature Pipeline** - вычисление фичей
6. **Model Training** - обучение моделей
7. **Model Registry** - управление версиями моделей
8. **Forecast Service** - онлайновое прогнозирование
9. **Forecast Storage** - хранение прогнозов
10. **Monitoring Service** - мониторинг качества
11. **Admin UI** - веб-интерфейс
12. **Orchestration** - оркестрация обучения

## Технологический стек

- **Backend**: Python 3.12, FastAPI
- **Frontend**: React 19, Next.js 14, TypeScript
- **ML**: PyTorch, LightGBM, CatBoost
- **Базы данных**: PostgreSQL, ClickHouse, Redis
- **Хранилище**: MinIO (S3-совместимое)
- **Очереди**: Kafka/Redpanda
- **Оркестрация**: Kubernetes, Docker
- **CI/CD**: GitHub Actions

## Быстрый старт

### Локальная разработка

1. Запуск инфраструктуры:
```bash
cd infrastructure
docker-compose up -d
```

2. Запуск сервисов (пример для одного сервиса):
```bash
cd backend/api_gateway
pip install -e .
uvicorn main:app --reload
```

### Развертывание в Kubernetes

1. Применение манифестов:
```bash
kubectl apply -f infrastructure/kubernetes/namespace.yaml
kubectl apply -f infrastructure/kubernetes/
```

2. Проверка статуса:
```bash
kubectl get pods -n forecast-system
```

## Документация API

После запуска API Gateway доступен по адресу:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Лицензия

MIT


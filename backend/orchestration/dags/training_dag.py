"""
DAG для периодического обучения моделей
Используется с Airflow или Dagster
"""
from datetime import datetime, timedelta
import httpx
from typing import Dict, Any


class TrainingDAG:
    """DAG для обучения моделей"""
    
    def __init__(self, model_training_url: str = "http://model-training:8006"):
        self.model_training_url = model_training_url
        self.http_client = httpx.AsyncClient()
    
    async def get_active_assets(self, asset_service_url: str) -> list:
        """Получение списка активных активов"""
        try:
            response = await self.http_client.get(
                f"{asset_service_url}/assets",
                params={"limit": 1000}
            )
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Error fetching assets: {e}")
        return []
    
    async def trigger_training(self, asset_id: str, model_id: str, model_type: str = "lightgbm"):
        """Запуск обучения модели"""
        try:
            response = await self.http_client.post(
                f"{self.model_training_url}/train",
                params={
                    "asset_id": asset_id,
                    "model_id": model_id,
                    "model_type": model_type
                }
            )
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Error triggering training: {e}")
        return None
    
    async def run_dag(self, asset_service_url: str, model_id: str, model_type: str = "lightgbm"):
        """Выполнение DAG"""
        print(f"Starting training DAG at {datetime.utcnow()}")
        
        # Получение активов
        assets = await self.get_active_assets(asset_service_url)
        print(f"Found {len(assets)} assets")
        
        # Запуск обучения для каждого актива
        results = []
        for asset in assets:
            asset_id = asset.get("id")
            if asset_id:
                print(f"Training model for asset {asset.get('ticker')} ({asset_id})")
                result = await self.trigger_training(asset_id, model_id, model_type)
                if result:
                    results.append({
                        "asset_id": asset_id,
                        "status": "started",
                        "result": result
                    })
                else:
                    results.append({
                        "asset_id": asset_id,
                        "status": "failed"
                    })
        
        print(f"DAG completed. Processed {len(results)} assets")
        return results
    
    async def close(self):
        """Закрытие соединений"""
        await self.http_client.aclose()


# Пример использования с Airflow
"""
from airflow import DAG
from airflow.operators.python import PythonOperator
from backend.orchestration.dags.training_dag import TrainingDAG

default_args = {
    'owner': 'forecast-team',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'model_training_dag',
    default_args=default_args,
    description='Периодическое обучение моделей',
    schedule_interval=timedelta(days=1),  # Ежедневно
    catchup=False,
)

def run_training():
    training_dag = TrainingDAG()
    import asyncio
    asyncio.run(training_dag.run_dag(
        asset_service_url="http://asset-service:8001",
        model_id="00000000-0000-0000-0000-000000000001",
        model_type="lightgbm"
    ))

training_task = PythonOperator(
    task_id='train_models',
    python_callable=run_training,
    dag=dag,
)
"""


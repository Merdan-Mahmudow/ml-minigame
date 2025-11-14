"""
Dagster job для обучения моделей
"""
from dagster import job, op, schedule, DefaultSensorStatus
from backend.orchestration.dags.training_dag import TrainingDAG
import asyncio


@op
def train_models_op(context):
    """Операция обучения моделей"""
    training_dag = TrainingDAG()
    
    # Параметры из конфигурации
    asset_service_url = context.op_config.get("asset_service_url", "http://asset-service:8001")
    model_id = context.op_config.get("model_id", "00000000-0000-0000-0000-000000000001")
    model_type = context.op_config.get("model_type", "lightgbm")
    
    # Запуск DAG
    results = asyncio.run(training_dag.run_dag(asset_service_url, model_id, model_type))
    
    context.log.info(f"Training completed for {len(results)} assets")
    return results


@job
def model_training_job():
    """Job для обучения моделей"""
    train_models_op()


@schedule(
    job=model_training_job,
    cron_schedule="0 2 * * *",  # Каждый день в 2:00
    default_status=DefaultSensorStatus.RUNNING,
)
def daily_training_schedule(context):
    """Расписание ежедневного обучения"""
    return model_training_job.run(
        run_config={
            "ops": {
                "train_models_op": {
                    "config": {
                        "asset_service_url": "http://asset-service:8001",
                        "model_id": "00000000-0000-0000-0000-000000000001",
                        "model_type": "lightgbm"
                    }
                }
            }
        }
    )


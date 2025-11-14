# Оркестрация обучения моделей

Этот модуль содержит DAG для оркестрации периодического обучения моделей.

## Использование с Airflow

1. Установите Airflow:
```bash
pip install apache-airflow
```

2. Скопируйте DAG в директорию Airflow:
```bash
cp backend/orchestration/dags/training_dag.py $AIRFLOW_HOME/dags/
```

3. DAG будет запускаться по расписанию (ежедневно)

## Использование с Dagster

1. Установите Dagster:
```bash
pip install dagster dagster-webserver
```

2. Запустите Dagster:
```bash
dagster-webserver -m backend.orchestration.dagster_job
```

3. Job будет доступен в веб-интерфейсе Dagster

## Конфигурация

Параметры можно настроить через переменные окружения или конфигурационные файлы оркестратора.


"""
BrasilBid — DAG de orquestração do pipeline de dados

Execução diária às 05:00 BRT (08:00 UTC):
  ingest_pncp → gen_dbt_profiles → dbt_run → dbt_test
"""
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator

PROJECT_DIR = "/opt/airflow/project"

default_args = {
    "owner": "brasilbid",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "email_on_failure": False,
}

with DAG(
    dag_id="brasilbid_pipeline",
    description="ETL PNCP → dbt run → dbt test",
    schedule="0 8 * * *",
    start_date=datetime(2025, 1, 1),
    catchup=False,
    default_args=default_args,
    tags=["brasilbid", "pncp", "dbt", "etl"],
) as dag:
    ingest = BashOperator(
        task_id="ingest_pncp",
        bash_command=f"cd {PROJECT_DIR} && python run_ingestion.py",
        env={"PYTHONPATH": PROJECT_DIR},
        append_env=True,
    )

    gen_profiles = BashOperator(
        task_id="gen_dbt_profiles",
        bash_command=f"cd {PROJECT_DIR} && python scripts/gen_profiles.py",
        env={"PYTHONPATH": PROJECT_DIR},
        append_env=True,
    )

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command=(
            f"cd {PROJECT_DIR} && "
            f"dbt run --project-dir dbt --profiles-dir dbt"
        ),
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=(
            f"cd {PROJECT_DIR} && "
            f"dbt test --project-dir dbt --profiles-dir dbt"
        ),
    )

    ingest >> gen_profiles >> dbt_run >> dbt_test

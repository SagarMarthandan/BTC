from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.models import Variable

# Set these in the Airflow UI (Admin -> Variables) or leave defaults here
PROJECT_DIR = Variable.get("DBT_PROJECT_DIR", "/path/to/dbt/project")
PROFILES_DIR = Variable.get("DBT_PROFILES_DIR", PROJECT_DIR)

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="dbt_daily_run",
    default_args=default_args,
    start_date=datetime(2024, 1, 1),
    schedule_interval="0 2 * * *",  # daily at 02:00
    catchup=False,
    max_active_runs=1,
    tags=["dbt"],
) as dag:
    dbt_deps = BashOperator(
        task_id="dbt_deps",
        bash_command=f"cd {PROJECT_DIR} && dbt deps --profiles-dir {PROFILES_DIR}",
    )

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command=f"cd {PROJECT_DIR} && dbt run --profiles-dir {PROFILES_DIR}",
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=f"cd {PROJECT_DIR} && dbt test --profiles-dir {PROFILES_DIR}",
    )

    dbt_deps >> dbt_run >> dbt_test

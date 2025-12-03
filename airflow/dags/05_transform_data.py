from airflow.sdk import dag, Asset
from datetime import datetime, timedelta
import os

# Define path to dbt project inside the container
DBT_PROJECT_DIR = "/opt/airflow/dags/dbt"
# Define path where pip installed dbt
DBT_BIN_DIR = "/home/airflow/.local/bin"

SNOWFLAKE_RAW_ASSET = Asset("snowflake://cde-core-telecom-data-lake/raw")


def get_dbt_env():
    from airflow.sdk import Connection

    conn = Connection.get("snowflake_default")

    extra_params = conn.extra_dejson

    return {
        # Map Airflow Connection fields to dbt Environment Variables
        "SNOWFLAKE_ACCOUNT": extra_params.get("account")
        or extra_params.get("account_name"),
        "SNOWFLAKE_USER": conn.login,
        "SNOWFLAKE_PASSWORD": conn.password,
        "SNOWFLAKE_ROLE": extra_params.get("role"),
        "SNOWFLAKE_WAREHOUSE": extra_params.get("warehouse"),
        "SNOWFLAKE_DATABASE": "core_telecom",
        "SNOWFLAKE_SCHEMA": "raw",
        # dbt Configuration
        "DBT_PROFILES_DIR": DBT_PROJECT_DIR,
        "PATH": f"{DBT_BIN_DIR}:{os.getenv('PATH', '/usr/bin:/bin')}",
    }


default_args = {
    "owner": "data_engineering",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}


@dag(
    dag_id="05_dbt_transformation",
    default_args=default_args,
    schedule=[SNOWFLAKE_RAW_ASSET],
    start_date=datetime(2025, 11, 20),
    catchup=False,
    tags=["transform", "dbt", "snowflake"],
)
def transform_data():
    from airflow.providers.standard.operators.bash import BashOperator

    dbt_env = get_dbt_env()

    # Install Deps
    dbt_deps = BashOperator(
        task_id="dbt_deps",
        bash_command=f"cd {DBT_PROJECT_DIR} && dbt deps",
        env=dbt_env,
    )

    # Run Models
    dbt_run = BashOperator(
        task_id="dbt_run", bash_command=f"cd {DBT_PROJECT_DIR} && dbt run", env=dbt_env
    )

    # Test Models
    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=f"cd {DBT_PROJECT_DIR} && dbt test",
        env=dbt_env,
    )

    dbt_deps >> dbt_run >> dbt_test

    # dbt_deps


dag = transform_data()

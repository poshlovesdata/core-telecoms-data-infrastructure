from datetime import datetime, timedelta
from airflow.sdk import dag, Asset
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
import os
from dotenv import load_dotenv

load_dotenv()

# Define Inputs (From Ingestion DAGs)
DEST_RAW_BUCKET = os.getenv("DEST_RAW_BUCKET")
POSTGRES_ASSET = Asset(f"s3://{DEST_RAW_BUCKET}/postgres")
S3_SOURCE_ASSET = Asset(f"s3://{DEST_RAW_BUCKET}/s3_source")
# Define Output (For Transformation DAG)
SNOWFLAKE_RAW_ASSET = Asset("snowflake://cde-core-telecom-data-lake/raw")

default_args = {
    "owner": "data_engineering",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}


@dag(
    dag_id="04_load_raw_snowflake",
    default_args=default_args,
    schedule=[POSTGRES_ASSET, S3_SOURCE_ASSET],
    start_date=datetime(2025, 11, 20),
    catchup=True,
    tags=["loading", "snowflake", "raw"],
)
def load_raw_data():
    # Load Static Data (Agents)
    load_agents = SQLExecuteQueryOperator(
        conn_id="snowflake_default",
        task_id="load_agents",
        sql="""
                                        USE DATABASE core_telecom;
                                        USE SCHEMA raw;
                                        BEGIN;
                                        TRUNCATE TABLE raw.agents;
                                        COPY INTO raw.agents
                                        FROM @raw.coretelecom_s3_stage/agents/
                                        FILE_FORMAT = (FORMAT_NAME = 'parquet_format')
                                        MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE
                                        PATTERN = '.*parquet';
                                        UPDATE agents SET _loaded_at = CURRENT_TIMESTAMP() WHERE _loaded_at IS NULL;
                                        COMMIT;
                                          """,
    )
    # Load Static Data (Customers)
    load_customers = SQLExecuteQueryOperator(
        task_id="load_customers",
        conn_id="snowflake_default",
        sql="""
            USE DATABASE core_telecom;
            USE SCHEMA raw;
            BEGIN;
            TRUNCATE TABLE customers;
            COPY INTO customers
            FROM @raw.coretelecom_s3_stage/customers/
            FILE_FORMAT = (FORMAT_NAME = 'parquet_format')
            MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE
            PATTERN = '.*parquet';
            UPDATE customers SET _loaded_at = CURRENT_TIMESTAMP() WHERE _loaded_at IS NULL;
            COMMIT;
        """,
    )

    # Load Dynamic Data (Web Forms)
    load_web_forms = SQLExecuteQueryOperator(
        task_id="load_web_forms",
        conn_id="snowflake_default",
        outlets=[SNOWFLAKE_RAW_ASSET],
        sql="""
            USE DATABASE core_telecom;
            USE SCHEMA raw;
            COPY INTO web_forms
            FROM @raw.coretelecom_s3_stage/web_forms/{{ logical_date.strftime('%Y') }}/{{ logical_date.strftime('%m') }}/{{ logical_date.strftime('%d') }}/
            FILE_FORMAT = (FORMAT_NAME = 'parquet_format')
            MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE
            ON_ERROR = CONTINUE;
            UPDATE web_forms SET _loaded_at = CURRENT_TIMESTAMP() WHERE _loaded_at IS NULL;
        """,
    )

    # Load Dynamic Data (Call Logs)
    load_call_logs = SQLExecuteQueryOperator(
        task_id="load_call_logs",
        conn_id="snowflake_default",
        outlets=[SNOWFLAKE_RAW_ASSET],
        sql="""
            USE DATABASE core_telecom;
            USE SCHEMA raw;
            COPY INTO call_logs
            FROM @raw.coretelecom_s3_stage/call_logs/{{ logical_date.strftime('%Y') }}/{{ logical_date.strftime('%m') }}/{{ logical_date.strftime('%d') }}/
            FILE_FORMAT = (FORMAT_NAME = 'parquet_format')
            MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE
            ON_ERROR = CONTINUE;
            UPDATE call_logs SET _loaded_at = CURRENT_TIMESTAMP() WHERE _loaded_at IS NULL;
        """,
    )

    # Load Dynamic Data (Social Media)
    load_social_media = SQLExecuteQueryOperator(
        task_id="load_social_media",
        conn_id="snowflake_default",
        outlets=[SNOWFLAKE_RAW_ASSET],
        sql="""
            USE DATABASE core_telecom;
            USE SCHEMA raw;
            COPY INTO social_media
            FROM @raw.coretelecom_s3_stage/social_media/{{ logical_date.strftime('%Y') }}/{{ logical_date.strftime('%m') }}/{{ logical_date.strftime('%d') }}/
            FILE_FORMAT = (FORMAT_NAME = 'parquet_format')
            MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE
            ON_ERROR = CONTINUE;
            UPDATE social_media SET _loaded_at = CURRENT_TIMESTAMP() WHERE _loaded_at IS NULL;
        """,
    )

    # Parallel Execution
    # [load_agents, load_customers, load_web_forms]
    [load_agents, load_customers, load_web_forms, load_call_logs, load_social_media]


dag = load_raw_data()

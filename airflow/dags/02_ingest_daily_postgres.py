from airflow.sdk import dag, task
from datetime import datetime, timedelta
import os

default_args = {
    "owner": "data_engineering",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}


@dag(
    dag_id="02_ingest_daily_postgres",
    default_args=default_args,
    schedule="@daily",
    start_date=datetime(2025, 11, 20),
    catchup=True,
    tags=["ingestion", "daily", "dynamic", "postgres", "database"],
)
def ingest_postgres_data():
    @task
    def extract_web_forms():
        """
        Extracts data from dynamic table: web_form_request_YYYY_MM_DD
        """

        import logging
        from common.s3_utils import S3Ingestor
        from dotenv import load_dotenv
        from airflow.providers.postgres.hooks.postgres import PostgresHook
        from airflow.sdk import get_current_context

        load_dotenv()
        logger = logging.getLogger("airflow.task")
        DEST_RAW_BUCKET = os.getenv("DEST_RAW_BUCKET")

        # Get airflow context for runtime variables

        try:
            context = get_current_context()

            logical_date = context["logical_date"]  # type: ignore
        except Exception:
            # Fallback for local testing (when no airflow context exists)
            logger.warning(
                "No Airflow context found. Using datetime.now() for local test."
            )
            logical_date = datetime.now()

        # Calculate dynamic table name using the logical date
        date_suffix = logical_date.strftime("%Y_%m_%d")
        table_name = f"web_form_request_{date_suffix}"
        schema = "customer_complaints"

        logger.info(f"Date: {logical_date}")
        logger.info(f"Target table: {schema}.{table_name}")

        pg_hook = PostgresHook(postgres_conn_id="postgres_source")

        # Check it table exists
        check_sql = f"""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_schema = '{schema}'
                AND table_name = '{table_name}'
                -- AND table_name = 'web_form_request_2025_11_20'
            );
        """

        # Check if True or False
        result = pg_hook.get_first(check_sql)
        logger.info(result[0])
        exists = result[0] if result else False

        if not exists:
            logger.warning(
                f"Table {table_name} doesn't exist for this date {date_suffix}"
            )
            return

        # Extract table data
        sql_query = f"SELECT * FROM {schema}.{table_name}"
        df = pg_hook.get_pandas_df(sql_query)
        print(df.head(10))
        logger.info(f"Extracted {len(df)} rows from {table_name}")

        # Upload to S3
        ingestor = S3Ingestor(DEST_RAW_BUCKET)

        # Partition Structure: /table/year/month/day
        y = logical_date.strftime("%Y")
        m = logical_date.strftime("%m")
        d = logical_date.strftime("%d")
        s3_key = f"web_forms/{y}/{m}/{d}/{table_name}_data.parquet"

        ingestor.upload_df_to_s3(df, s3_key)

    extract_web_forms()


dag = ingest_postgres_data()

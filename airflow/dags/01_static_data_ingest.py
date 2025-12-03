from datetime import datetime, timedelta
from airflow.sdk import dag, task
from airflow.providers.google.suite.hooks.sheets import GSheetsHook
from common.utils import task_failure_alert
import os
import re
import time


default_args = {"owner": "data_engineering", "on_failure_callback": task_failure_alert}


@dag(
    dag_id="01_ingest_static_data",
    default_args=default_args,
    start_date=datetime.now() - timedelta(days=1),
    catchup=False,
    tags=["ingestion", "static"],
)
def ingest_google_sheets():
    @task
    def extract_agent_sheet():
        import pandas as pd

        from common.s3_utils import S3Ingestor
        from dotenv import load_dotenv

        load_dotenv()

        DEST_RAW_BUCKET = os.getenv("DEST_RAW_BUCKET")
        GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
        hook = GSheetsHook(gcp_conn_id="google_cloud_conn")

        values = hook.get_values(spreadsheet_id=GOOGLE_SHEET_ID, range_="agents")

        if not values:
            raise ValueError("No data found in Google Sheet!")

        df = pd.DataFrame(values[1:], columns=values[0])

        def clean(col_name):
            # Lowercase, strip whitespace, replace spaces/special chars with underscore
            return re.sub(r"[^a-zA-Z0-9]", "_", str(col_name).strip().lower())

        df.columns = [clean(c) for c in df.columns]

        # Instatiate S3 Ingestor Class
        ingestor = S3Ingestor(DEST_RAW_BUCKET)
        ingestor.upload_df_to_s3(df, "agents/agents.parquet")

    @task
    def extract_customers_s3():
        """
        Ingest static customers.csv from S3 Source.
        """
        import pandas as pd
        import logging
        from common.s3_utils import S3Ingestor
        from dotenv import load_dotenv
        import boto3

        load_dotenv()

        DEST_RAW_BUCKET = os.getenv("DEST_RAW_BUCKET")
        SOURCE_RAW_BUCKET = os.getenv("SOURCE_RAW_BUCKET")
        AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
        AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
        AWS_DEFAULT_REGION = os.getenv("AWS_DEFAULT_REGION")

        logger = logging.getLogger("airflow.task")
        s3 = boto3.client(
            "s3",
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_DEFAULT_REGION,
        )
        source_key = "customers/customers_dataset.csv"
        local_file = "/tmp/customers_temp.csv"

        logger.info(f"Starting download from S3://{SOURCE_RAW_BUCKET}/{source_key}")
        start_time = time.time()
        file_size = 0

        try:
            # Download to tmp file
            s3.download_file(
                Bucket=SOURCE_RAW_BUCKET, Key=source_key, Filename=local_file
            )

            duration = time.time() - start_time
            file_size = os.path.getsize(local_file) / (1024 * 1024)  # MB
            logger.info(
                f"Download complete: {file_size:.2f}MB in {duration:.2f} seconds"
            )

            try:
                # Read with PyArrow Engine
                logger.info("Parsing CSV with PyArrow")
                df = pd.read_csv(local_file, engine="pyarrow")
                logger.info(f"Parsed {len(df)} rows.")
            except Exception as e:
                logger.warning(f"PyArrow Engine failed: {e}")
                logger.info("Falling back to C engine")
                # Read CSV with default engine
                df = pd.read_csv(
                    local_file,
                    engine="c",
                    on_bad_lines="warn",
                    quotechar='"',
                    escapechar="\\",
                )
                logger.info(f"Succesfully parsed CSV. Row Count: {len(df)}")

            # Upload to Raw Zone
            ingestor = S3Ingestor(DEST_RAW_BUCKET)
            ingestor.upload_df_to_s3(
                df=df, s3_key="customers/customers_dataset.parquet"
            )
        finally:
            if os.path.exists(local_file):
                os.remove(local_file)
                logger.info(f"Cleared temp file: {local_file} : {file_size:.2f}MB")

    extract_agent_sheet()
    extract_customers_s3()


dag = ingest_google_sheets()

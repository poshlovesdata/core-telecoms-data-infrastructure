# from pendulum import datetime
from datetime import datetime, timedelta
from airflow.sdk import dag, task
from airflow.providers.google.suite.operators.sheets import (
    GoogleSheetsCreateSpreadsheetOperator,
)
from airflow.providers.google.suite.hooks.sheets import GSheetsHook
from typing import Final
import boto3
import os
import logging
import pandas as pd
from dotenv import load_dotenv
from io import BytesIO
import re
from common.s3_utils import S3Ingestor

load_dotenv()

DEST_RAW_BUCKET = "core-telecoms-dev-raw"
SOURCE_RAW_BUCKET = "core-telecoms-data-lake"
aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
region_name = os.getenv("AWS_DEFAULT_REGION")

# sheet_id_env: str | None = os.getenv('GOOGLE_SHEET_ID')
sheet_id_env: str | None = "17IXo7TjDSSHaFobGG9hcqgbsNKTaqgyctWGnwDeNkIQ"

# GOOGLE_SHEET_ID = '17IXo7TjDSSHaFobGG9hcqgbsNKTaqgyctWGnwDeNkIQ'

default_args = {
    "owner": "data_engineering",
    "retries": 1,
}


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
        if sheet_id_env is None:
            raise ValueError(
                "Environment variable GOOGLE_SHEET_ID must be set and non-empty."
            )

        hook = GSheetsHook(gcp_conn_id="google_cloud_conn")
        GOOGLE_SHEET_ID: Final[str] = sheet_id_env
        values = hook.get_values(spreadsheet_id=GOOGLE_SHEET_ID, range_="agents")

        if not values:
            raise ValueError("No data found in Google Sheet!")

        df = pd.DataFrame(values[1:], columns=values[0])

        def clean(col_name):
            # Lowercase, strip whitespace, replace spaces/special chars with underscore
            return re.sub(r"[^a-zA-Z0-9]", "_", str(col_name).strip().lower())

        df.columns = [clean(c) for c in df.columns]

        # print(df.head(10))

        ingestor = S3Ingestor(DEST_RAW_BUCKET)
        ingestor.upload_df_to_s3(df, "agents/agents.parquet")

    extract_agent_sheet()


dag = ingest_google_sheets()

from datetime import datetime, timedelta
from airflow.sdk import dag, task
import boto3
import os
import logging
import pandas as pd
from dotenv import load_dotenv
from common.utils import get_source_s3
from common.utils import get_logical_date
from common.s3_utils import S3Ingestor


load_dotenv()


DEST_RAW_BUCKET = os.getenv("DEST_RAW_BUCKET")
SOURCE_RAW_BUCKET = os.getenv("SOURCE_RAW_BUCKET")

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_DEFAULT_REGION = os.getenv("AWS_DEFAULT_REGION")

default_args = {
    "owner": "data_engineering",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}


@dag(
    dag_id="03_ingest_daily_s3_sources",
    default_args=default_args,
    schedule="@daily",
    start_date=datetime(2025, 11, 20),
    catchup=True,
    tags=["ingestion", "daily", "dynamic", "s3"],
)
def ingest_daily_s3():
    logger = logging.getLogger("airflow.tasks")

    @task
    def ingest_call_center():
        """Ingest call logs data. call_logs_day_YYYY-MM-DD.csv"""
        s3 = get_source_s3()

        logical_date = get_logical_date()

        # Calculate dynamic source key using the logical date
        date_suffix = logical_date.strftime("%Y-%m-%d")
        source_key = f"call logs/call_logs_day_{date_suffix}.csv"
        logger.info(f"Fetching s3://{SOURCE_RAW_BUCKET}/{source_key}")

        try:
            obj = s3.get_object(Bucket=SOURCE_RAW_BUCKET, Key=source_key)
            print(obj["Body"])

            df = pd.read_csv(obj["Body"])
            logger.info(f"Successfully streamed {len(df)} rows.")
            print(df.head(10))

            ingestor = S3Ingestor(DEST_RAW_BUCKET)

            y = logical_date.strftime("%Y")
            m = logical_date.strftime("%m")
            d = logical_date.strftime("%d")
            # Set destination key with partitioning
            destination_key = (
                f"call_logs/{y}/{m}/{d}/call_log_day_{date_suffix}.parquet"
            )
            ingestor.upload_df_to_s3(df, destination_key)
        except s3.exceptions.NoSuchKey as e:
            logger.warning(f"{source_key} not found")

    @task
    def ingest_social_media():
        """Ingest social media. media_complaint_day_YYYY-MM-DD.json"""
        s3 = get_source_s3()
        logical_date = get_logical_date()
        date_suffix = logical_date.strftime("%Y-%m-%d")

        source_key = f"social_medias/media_complaint_day_{date_suffix}.json"

        try:
            obj = s3.get_object(Bucket=SOURCE_RAW_BUCKET, Key=source_key)

            df = pd.read_json(obj["Body"])
            ingestor = S3Ingestor(DEST_RAW_BUCKET)

            # Set destination key with partitioning
            y = logical_date.strftime("%Y")
            m = logical_date.strftime("%m")
            d = logical_date.strftime("%d")

            destination_key = (
                f"social_media/{y}/{m}/{d}/media_complaint_day_{date_suffix}.parquet"
            )
            ingestor.upload_df_to_s3(df, destination_key)
        except s3.exceptions.NoSuchKey as e:
            logger.warning(f"{source_key} not found")

    ingest_call_center()
    ingest_social_media()


dag = ingest_daily_s3()

import boto3
import pandas as pd
import logging
from dotenv import load_dotenv
import os
import re
from datetime import datetime
from io import BytesIO

load_dotenv()
logger = logging.getLogger("airflow.task")


class S3Ingestor:
    """
    Utility to handle ingestion to S3 bucket.
    """

    def __init__(self, bucket_name: str) -> None:
        self.bucket_name = bucket_name

        try:
            self.s3_client = boto3.client(
                "s3",
                aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
                region_name=os.getenv("AWS_DEFAULT_REGION"),
            )
        except Exception as e:
            logger.error("Failed to initialize AWS S3")
            raise e
        return None

    def _standardize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Function to standardize column names (spaces, capital letters) before converting to Parquet
        """

        def clean_column(col_name):
            # Lowercase, strip whitespace, replace spaces/special chars with underscore
            return re.sub(r"[^a-zA-Z0-9]", "_", str(col_name).strip().lower())

        df.columns = [clean_column(c) for c in df.columns]
        return df

    def upload_df_to_s3(self, df: pd.DataFrame, s3_key: str) -> str:
        """
        Converts Dataframe to Parquet and uploadds to S3 bucket
        Includes Metadata column for ingestion time
        """
        try:
            if df.empty:
                logger.warning(
                    f"Dataframe for {s3_key} is empty. Uploading empty file "
                )

            # Add column for ingestion time
            df["ingested_at"] = datetime.now()

            # Standardize column names for parquet
            df = self._standardize_columns(df)

            # Convert to parquet
            out_buffer = BytesIO()
            df.to_parquet(
                out_buffer, index=False, engine="pyarrow", compression="snappy"
            )

            print(df.head(10))

            # Upload
            self.s3_client.put_object(
                Bucket=self.bucket_name, Key=s3_key, Body=out_buffer.getvalue()
            )

            s3_path = f"s3://{self.bucket_name}/{s3_key}"
            logger.info(
                f"Uploaded {len(df)} rows to {s3_path} (Cols: {list(df.columns)})"
            )
            return s3_path
        except Exception as e:
            logger.error(f"Failed to upload to S3: {e}")
            raise e

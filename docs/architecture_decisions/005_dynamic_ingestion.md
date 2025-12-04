# Day 5: Dynamic Ingestion Architecture

## 1. Executive Summary

The goal of Day 5 was to implement the **Incremental Extraction layer**. Unlike static data, these sources generate new data daily. I implemented dynamic Airflow DAGs that use the `logical_date` to target specific daily slices of data from Postgres and S3.

## 2. Key Design Decisions

### A. Idempotency via Logical Dates

- **Context:** Daily data is stored in files/tables with date suffixes (e.g., `_2025_11_20`).
- **Decision:** Used Airflow's `logical_date` to calculate the target path.
- **Impact:** Pipeline is fully **idempotent**.

  - Re-running the DAG for "Nov 20th" today correctly targets that date, not today's data.
  - Enables safe backfilling and replays.

### B. Resilience: Automated Backfilling

- **Context:** The project requirements specified extracting data from a historical start date (Nov 20th, 2025), not just "today onwards".

- **Decision:** Enabled Airflow's Catchup mechanism.

  - `start_date = datetime(2025, 11, 20)`

  - `catchup = True`

- **Justification:**

  - **Completeness:** Automatically generates DAG runs for every day between the start date and the current date, ensuring no historical data gaps.

  - **Consistency:** The exact same code logic handles both "history" (backfill) and "future" (scheduled runs), adhering to the DRY principle.

### C. Postgres Extraction Pattern

- **Challenge:** Source Postgres table name changes daily (`Web_form_request_YYYY_MM_DD`).
- **Solution:**

  - **Dynamic SQL:** Construct table names using f-strings: `f"web_form_request_{logical_date.strftime('%Y_%m_%d')}"`
  - **Pre-Flight Check:** Query `information_schema.tables` to ensure table exists.
  - **Soft Fail:** Missing tables log a warning and skip (Success state), handling late-arriving data gracefully.

### D. S3 Extraction Pattern

- **Challenge:** Source logs stored as daily CSV/JSON files.
- **Solution:**

  - Used `boto3` with `s3.download_file` + `pd.read_csv`.
  - **Performance Optimization:**

    - Streaming via `obj['Body']` for smaller files (<300MB) to reduce I/O latency.
    - Leveraged reusable `S3Ingestor` for schema hygiene (sanitized column names) and metadata injection (`_ingested_at`).

### E. Partitioning Strategy

- **Context:** Store data in S3 Raw for efficient downstream processing and easy navigation.
- **Decision:** Partitioned by **Year/Month/Day**.

  - **Path:** `s3://.../raw/web_forms/YYYY/MM/DD/data.parquet`

- **Justification:**

  - **Simplicity:** Cleaner, easier to browse path structure in AWS Console.
  - **Performance:** Enables partition pruning in Snowflake/External Tables using path prefixes.

## 3. Next Steps

With the Data Lake (Raw Layer) fully populated, the next phase is **Data Loading (Day 6)**. I will configure Snowflake to ingest these Parquet files from S3 into the RAW schema tables.

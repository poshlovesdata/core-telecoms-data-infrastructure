# Day 4: Static Data Ingestion Architecture

## 1. Executive Summary

The goal of Day 4 was to implement the **Extract & Load (EL)** pipeline for static reference datasets. I successfully built an Airflow DAG (`01_ingest_static_data`) that ingests:

- **Agent Data:** From a private Google Sheet.
- **Customer Data:** From a messy CSV in an external S3 bucket.

The solution enforces a **Schema-On-Write** approach, converting all raw inputs into standardized, compressed Parquet files in the S3 Raw Zone.

## 2. Key Design Decisions

### A. Ingestion Pattern: Modular Utility (S3Ingestor)

- **Context:** Pipeline logic (download → parse → clean → upload) is repetitive across multiple sources.
- **Decision:** Encapsulated logic into a reusable class `common.s3_utils.S3Ingestor`.
- **Justification:**

  - **DRY Principle:** Prevents code duplication across DAGs.
  - **Standardization:** Enforces uniform Parquet settings (`Snappy` compression, PyArrow engine) and metadata injection (`_ingested_at`) for all files.

### B. Performance Strategy: PyArrow with Fallback

- **Context:** `Customers.csv` is large and contains messy formatting (multiline addresses).
- **Challenge:** Pandas parser is slow; PyArrow engine crashes on malformed rows.
- **Decision:** Implemented an Optimistic Performance Pattern.

  - **Try Fast:** Parse with `engine="pyarrow"` (multithreaded, ~10x faster).
  - **Catch & Recover:** On `ArrowInvalid`, fallback to standard C engine with `on_bad_lines='warn'`.

- **Impact:** Maximizes speed for clean files while ensuring stability for messy legacy data.

### C. Technical Hygiene: Schema Standardization

- **Context:** Source headers contain trailing spaces causing downstream failures.
- **Decision:** Automated column sanitization during extraction.
- **Logic:** `re.sub(r'[^a-zA-Z0-9]', '_', col.lower().strip())`
- **Justification:** Raw layer remains immutable; structure must be valid for downstream consumption.

### D. File Format: Parquet vs. CSV/JSON

- **Context:** Project requirements specify raw data storage.
- **Decision:** Convert all inputs to Parquet immediately.
- **Justification:**

  - **Cost:** Snappy-compressed Parquet reduces S3 storage costs by ~60%.
  - **Type Safety:** Preserves schema information, preventing type inference errors in Snowflake.

## 3. Infrastructure & Security

| Component     | Configuration         | Note                                                                 |
| ------------- | --------------------- | -------------------------------------------------------------------- |
| Google Sheets | GoogleSheetsHook      | Authenticated via Service Account JSON mounted in Docker.            |
| S3 Source     | boto3 Client          | Authenticated via AWS IAM User keys injected from host `.env`.       |
| Network       | download_file to /tmp | Decouples network latency from CPU parsing. Temp files auto-cleaned. |

## 4. Next Steps

With static data ingestion complete and the reusable **S3Ingestor** tested, the next phase is **Dynamic Ingestion (Day 5)**. I will implement the logic to handle daily incremental loads from Postgres and S3 log streams.

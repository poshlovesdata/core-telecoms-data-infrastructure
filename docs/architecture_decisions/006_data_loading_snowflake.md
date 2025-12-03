# Day 6: Data Loading Architecture

## 1. Executive Summary

The goal of Day 6 was to implement the **Loading layer (L in ELT)**. I configured the **Snowflake Data Warehouse** to ingest Parquet files from the S3 Data Lake into the **RAW schema tables** using a secure, automated pipeline.

## 2. Key Design Decisions

### A. Authentication: Storage Integration (Secure Handshake)

- **Context:** Snowflake needs permission to read files from the private S3 Data Lake bucket.
- **Anti-Pattern:** Hardcoding AWS Access Keys directly in `CREATE STAGE` is insecure.
- **Decision:** Implemented a **Storage Integration** object.
- **Mechanism:**

  - **AWS:** Created IAM Role (`core-telecoms-snowflake-role`) with read access to the Data Lake bucket.
  - **Snowflake:** Created Storage Integration (`cde_s3_int`) pointing to the Role ARN.
  - **Handshake:** Retrieved `STORAGE_AWS_IAM_USER_ARN` and `STORAGE_AWS_EXTERNAL_ID` from Snowflake and updated AWS Role Trust Policy to allow only that specific Snowflake identity.

- **Benefit:** Zero long-lived credentials; authentication handled seamlessly via AWS STS.

### B. Loading Strategy: COPY INTO vs. Snowpipe

- **Context:** Daily batch loads are required.
- **Options:**

  - **Snowpipe:** Event-driven, excellent for streaming.
  - **COPY INTO (Batch):** Scheduled SQL loading.

- **Decision:** Selected `COPY INTO` orchestrated by Airflow (`SQLExecuteQueryOperator`).
- **Justification:**

  - **Cost Control:** Snowpipe costs per file; batch loading utilizes warehouse credits efficiently.
  - **Orchestration Dependency:** Ensures transformations run only after successful load, managed via Airflow.

### C. Schema Handling: Explicit Tables vs. Schema-on-Read

- **Context:** Parquet files contain embedded schema metadata.
- **Decision:** Defined explicit DDL for raw tables with `MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE`.
- **Justification:**

  - **Contract:** Guarantees `_ingested_at` exists.
  - **Flexibility:** Column reordering in Parquet files won't break the load.

### D. Idempotency: Partition Pruning

- **Challenge:** Prevent duplicate ingestion if DAG is re-run for past dates.
- **Solution:** Dynamically target specific S3 partitions based on Airflow `logical_date`:

  ```sql
  FROM @cde_s3_stage/raw/web_forms/{{ logical_date.strftime('%Y') }}/{{ logical_date.strftime('%m') }}/{{ logical_date.strftime('%d') }}/
  ```

- **Impact:** Re-running for "Nov 20th" reads only that folder, preventing duplication.

## 3. Infrastructure & Configuration

| Component          | Resource Name                | Note                                                        |
| ------------------ | ---------------------------- | ----------------------------------------------------------- |
| AWS Role           | core-telecoms-snowflake-role | Trusts Snowflake's IAM User/External ID.                    |
| Snowflake Stage    | cde_s3_stage                 | External stage pointing to `s3://core-telecoms-data-lake/`. |
| Airflow Connection | snowflake_default            | Configured via `AIRFLOW_CONN_SNOWFLAKE_DEFAULT`.            |

## 4. Next Steps

With the data successfully loaded into **Snowflake RAW tables**, the Data Lakehouse is populated. The final phase is **Transformation (Day 7)**. I will use **dbt** to apply business logic, clean the data, and model it into business-ready Marts.

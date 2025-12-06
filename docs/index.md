# Core Telecoms: Unified Customer Data Platform

A production-grade ELT pipeline designed to unify customer experience data, reduce churn, and enable 360° analytics.

## Executive Summary

Core Telecoms, a leading US telecommunications provider, faced fragmented customer data across Postgres databases (Web Forms), CSV dumps (Call Center Logs), and JSON streams (Social Media), which delayed insights and increased churn.

This project delivers a **Unified Data Platform** that:

- Ingests data from 5 disparate sources into a centralized Data Lake.
- Transforms messy, raw logs into clean, business-ready Marts using a Medallion Architecture.
- Automates the lifecycle with Airflow 3.0 and GitHub Actions.
- Secures PII and infrastructure using IAM Roles and S3 Encryption.

**Business Impact:** Reduces report generation time from days to minutes, providing a single source of truth for Customer Success teams.

## Architecture

![Core Telecoms Architecture](./images/core-telecoms-dark.drawio.png)

The platform follows a **Lakehouse Architecture**, decoupling storage (S3) from compute (Snowflake) for scalability and cost efficiency.

### High-Level Data Flow

```
Sources -> Ingestion (Airflow) -> Data Lake (S3) -> Warehouse (Snowflake) -> Transformation (dbt) -> BI / Analytics
```

- **Extract:** Python-based Airflow DAGs pull data from Spreadsheets, APIs, and Databases.
- **Load:** Parquet files are loaded into Snowflake RAW tables via COPY INTO.
- **Transform:** dbt models clean (Bronze), join (Silver), and aggregate (Gold) data.

## Documentation

- [Management Presentation](https://gamma.app/docs/CoreTelecoms-Presentation-ehc29r49ddlllp3?mode=doc) (Slide Deck)

- [Data Lineage/Documentation](https://poshlovesdata.github.io/core-telecoms-data-infrastructure/dbt/#!/overview)

### Architecture Decision Records (ADRs)

Explore the detailed engineering decisions behind this platform:

- [001 - Infrastructure Setup](./architecture_decisions/001_infrastructure_setup.md): Cloud foundation, networking, and security.

- [002 - Compute & Security](./architecture_decisions/002_compute_and_security.md): Snowflake vs. Redshift and Identity Management.

- [003 - Orchestration](./architecture_decisions/003_orchestration_setup.md): Airflow 3.0 configuration and event-driven scheduling.

- [004 - Static Ingestion](./architecture_decisions/004_static_data_ingestion.md): Handling Google Sheets and messy CSVs.

- [005 - Dynamic Ingestion](./architecture_decisions/005_dynamic_ingestion.md): Incremental extraction patterns for DBs and Logs.

- [006 - Data Loading](./architecture_decisions/006_data_loading_snowflake.md): Secure Snowflake-S3 integration.

- [007 - Transformation](./architecture_decisions/007_transformation_dbt.md): dbt Medallion architecture and data modeling.

- [008 - CI/CD & Automation](./architecture_decisions/008_cicd_automation.md): DevOps pipelines and quality gates.

### Live Execution Graph (Event-Driven)

![Alt text](./images/image.png)

This pipeline uses Airflow Assets (Data-Aware Scheduling) instead of brittle time-based dependencies. The Transformation layer only runs once the Snowflake data is confirmed loaded.

## Tech Stack & Decisions

| Component      | Technology         | Senior Engineering Decision                                                                                                                                                                                              |
| -------------- | ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Infrastructure | Terraform          | Fully modular IaC. S3 Native State Locking for concurrency safety. Zero-click deployment.                                                                                                                                |
| Orchestration  | Apache Airflow 3.0 | Adopted v3.0 (API Server architecture). LocalExecutor for efficient resource usage. Implemented Data-Aware Scheduling (Assets) for event-driven dependencies (Ingest -> Load -> Transform), eliminating race conditions. |
| Data Lake      | AWS S3 (Parquet)   | Schema-on-Write via PyArrow. Snappy compression reduces storage costs ~60%. Lifecycle Policies enabled for auto-archiving.                                                                                               |
| Warehouse      | Snowflake          | Separation of storage/compute. Connected via Storage Integrations (no hardcoded keys).                                                                                                                                   |
| Transformation | dbt Core           | Medallion Architecture (Bronze/Silver/Gold). Outputs: Star Schema + One Big Table (OBT).                                                                                                                                 |
| Observability  | Slack Integration  | Real-time failure alerts sent to Slack channels via Airflow callbacks (on_failure_callback).on_failure_callback.                                                                                                         |
| CI/CD          | GitHub Actions     | Automated Quality Gates: `ruff` (Python), `terraform validate`, and `dbt parse` on every PR. Docker build/push on merge.                                                                                                 |

## Project Structure

```
├── airflow/               # Orchestration Layer
│   ├── dags/              # Python DAGs (Extract & Load)
│   ├── common/            # Reusable Python Utilities (S3Ingestor)
│   ├── Dockerfile         # Custom Airflow 3.0 Image
│   └── docker-compose.yaml # Local Dev Environment
├── dbt/                   # Transformation Layer
│   ├── models/            # SQL Models (Staging, Int, Marts)
│   ├── profiles.yml       # Connection Config (Env Var Bridge)
│   └── dbt_project.yml    # Project Config
├── terraform/             # Infrastructure Layer
│   ├── main.tf            # AWS Resource Definitions
│   ├── iam.tf             # Least Privilege Roles & Policies
│   └── modules/           # Reusable Modules (VPC, S3)
├── scripts/               # Helper Scripts (Snowflake DDL)
└── docs/                  # Architecture Decision Records (ADRs)
```

## Getting Started

### Prerequisites

- Docker & Docker Compose
- AWS Account (Free Tier friendly)
- Snowflake Account (Standard Edition)
- Google Cloud Project (with Sheets API enabled)
- Terraform CLI (v1.5+)
- Slack Workspace (for alerts)

### 1. Provision Infrastructure

```bash
cd terraform
terraform init
terraform apply -var="snowflake_account_arn=..."
# See docs/006 for Snowflake handshake steps
```

### 2. Configure Data Warehouse

Run the SQL scripts to initialize Snowflake RBAC, Warehouses, and Storage Integrations.

1. Account Setup: Run `scripts/snowflake/01_snowflake_setup.sql` as ACCOUNTADMIN.

2. Raw Layer & Handshake: Run `scripts/snowflake/02_setup_raw_layer.sql`.

- Note: Ensure you update the STORAGE_AWS_ROLE_ARN with the output from Terraform.

### 2. Configure Local Environment

Create `.env` in `airflow/`:

```
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
AWS_DEFAULT_REGION=..
GOOGLE_SHEET_ID=..
AIRFLOW_CONN_SNOWFLAKE_DEFAULT=snowflake://...
AIRFLOW_CONN_SLACK_DEFAULT=slack://xoxb-your-token...
```

### 3. Launch the Platform

```bash
cd airflow
docker-compose up --build -d
```

Access Airflow UI at `http://localhost:8080` (User: admin / Pass: airflow)

### 4. Run the Pipeline

- Trigger Ingestion DAGs: `01_static`, `02_postgres`, `03_s3` → populate S3
- Trigger Loading DAG: `04_load_raw` → hydrate Snowflake
- Trigger Transformation DAG: `05_dbt` → build Marts

## Security & Governance

- **Network Security:** S3 buckets enforce `block_public_acls`.
- **Identity:** Hybrid Identity Model: IAM Roles for Production, IAM Users for Local Dev.
- **Secrets:** Zero secrets in Git; all credentials via Environment Variables or AWS SSM Parameter Store.
- **Metadata:** `_ingested_at` and `_loaded_at` timestamps for full lineage traceability.
- **FinOps:** Lifecycle Rules automatically transition data to Infrequent Access (30 days) and Glacier (90 days) to optimize long-term storage costs.
- **Resilience:** Pipeline enables catchup=True to automatically backfill historical data from the source inception date, ensuring no gaps in data coverage.

## Data Quality (dbt Tests)

Pipeline enforces strict data contracts:

- **Uniqueness:** Primary keys (`customer_id`, `complaint_id`) must be unique.
- **Not Null:** Critical foreign keys required.
- **Accepted Values:** Status columns validated (`Resolved`, `Open`).

Run tests manually:

```bash
docker exec -it airflow-apiserver bash -c "cd dbt && dbt test"
```

## Author

**Oluwapelumi Oshundiya** – Data Platform Engineer
[LinkedIn](www.linkedin.com/poshlovesdata)

_Built as a Capstone Project demonstrating Data Engineering competencies._

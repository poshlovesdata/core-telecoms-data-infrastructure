# Day 3: Orchestration & Local Environment Architecture

## 1. Executive Summary

The goal of Day 3 was to establish the local orchestration environment. I containerized **Apache Airflow 3.0** using Docker and configured it to interact securely with the AWS (S3) and Snowflake resources provisioned in previous phases.

The architecture prioritizes **Developer Experience (DevEx)** and **Resource Efficiency** for a single-machine setup while adopting the latest Airflow 3.0 architectural standards (AIP-44).

## 2. Key Design Decisions

### A. Airflow Version

- **Context:** Airflow 3.0 introduces architectural changes, separating the Execution API Server from the Scheduler/Webserver.
- **Decision:** Adopted Airflow 3.0.6.
- **Justification:**

  - **Future-Proofing:** Building on the latest standard avoids immediate technical debt.
  - **Workload Isolation:** Leverages the new `api-server` component, aligning with AIP-44 standards.

### B. Executor Strategy: LocalExecutor vs. CeleryExecutor

- **Context:** Production recommends CeleryExecutor or KubernetesExecutor, which require message brokers and separate workers.
- **Constraint:** Local MacBook (~16GB RAM) must run Snowflake/AWS connectors simultaneously.
- **Decision:** Selected LocalExecutor.
- **Justification:**

  - **Resource Efficiency:** Eliminates redis, airflow-worker, and flower containers (~4GB RAM saved).
  - **Simplicity:** Tasks run as subprocesses on the scheduler/machine.
  - **Parity:** Sufficient parallelism for non-distributed capstone workload.

### C. Hybrid Cloud Authentication

- **Context:** Airflow container needs authentication with AWS S3 and Google Cloud (Sheets API).
- **Decision:** Implemented Environment Variable Injection.

  - **AWS:** Injected `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` from host `.env` file.
  - **GCP:** Mounted `google_service_account.json` to `/opt/airflow/secrets/`.

- **Security Measure:** Added `.env` and `secrets/*.json` to `.gitignore`.

## 3. Infrastructure Components

| Service       | Role                | Configuration                                           |
| ------------- | ------------------- | ------------------------------------------------------- |
| Postgres      | Metadata Store      | v13, Alpine-based for size. Persisted via Docker Volume |
| API Server    | Execution Interface | Airflow 3.0 component. Exposes port 8080.               |
| Scheduler     | Orchestrator        | LocalExecutor mode. Handles task triggering.            |
| Triggerer     | Async Events        | Handles Deferrable Operators (Sensors).                 |
| DAG Processor | Parser              | Decoupled parsing logic for stability.                  |

## 4. Next Steps

With the engine running, the next phase is **Data Ingestion (Day 4)**. I will write the first DAG to extract data from the "Static" sources (Google Sheets) and load it into the S3 Raw Zone.

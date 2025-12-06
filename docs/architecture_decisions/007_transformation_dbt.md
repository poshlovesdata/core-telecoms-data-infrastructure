# Day 7: Data Transformation Architecture

## 1. Executive Summary

The goal of Day 7 was to implement the **Transformation layer (T in ELT)**. I integrated **dbt (data build tool)** into the Airflow pipeline to clean, standardize, and model raw data residing in Snowflake.

The solution adopts a **Medallion Architecture (Bronze/Silver/Gold)** to separate technical hygiene from business logic, culminating in both a **Star Schema** and a **One Big Table (OBT)** to serve diverse analytical needs.

![](../images/dbt_lineage.png)

## 2. Key Design Decisions

### A. Architecture: Medallion Schema (Bronze → Silver → Gold)

- **Context:** Raw data is messy and normalized; business users need clean, denormalized data.
- **Decision:** Implemented a 3-layer architecture:

  - **Staging (Bronze):** 1:1 views of raw tables. Focus on technical hygiene (renaming columns, casting types, standardizing formatting like lowercase emails).
  - **Intermediate (Silver):** "Engine Room". Integrates disparate sources (Web, Call, Social) into a unified `int_complaints_unioned` model and enriches with dimensions (`int_complaints_enriched`).
  - **Marts (Gold):** "Product". Exposes business-ready entities (`dim_customers`, `fct_complaints`).

### B. Modeling Strategy: Hybrid (Star Schema + OBT)

- **Context:** Different tools have different needs:

  - PowerBI/Looker: Prefer Star Schemas.
  - Tableau/Excel/Ad-hoc SQL: Prefer denormalized tables.

- **Decision:** Built both.

  - **Star Schema:** `dim_customers`, `dim_agents`, `fct_complaints`.
  - **OBT:** `obt_complaints_overview` (single wide table with all dimensions pre-joined).

- **Justification:** Maximizes flexibility without duplicating logic, since OBT selects from the enriched intermediate model.

### C. Schema Management: Custom Schemas vs. Public

- **Context:** dbt defaults to the public schema.
- **Challenge:** Public schema in Snowflake is owned by `ACCOUNTADMIN`, causing permission errors.
- **Decision:** Configured dbt (`profiles.yml`) to target a dedicated `ANALYTICS` schema.
- **Benefit:** Cleaner separation of duties. Core data engineering role owns the `ANALYTICS` namespace, preventing permission conflicts.

### D. Data Quality & Lineage

- **Decision:** Propagated metadata through all layers:

  - `_ingested_at`: Preserved from S3 Raw to Gold (extraction time).
  - `_loaded_at`: Preserved from Snowflake Raw to Gold (warehouse load time).
  - `_enriched_at`: Added in Intermediate layer (transformation time).

- **Impact:** Full lineage observability; trace records from dashboard back to source extraction time.

## 3. Infrastructure Components

| Component      | Configuration      | Note                                                                                                                               |
| -------------- | ------------------ | ---------------------------------------------------------------------------------------------------------------------------------- |
| dbt Core       | v1.8+ (Dockerized) | Installed inside Airflow image for simplified orchestration.                                                                       |
| Orchestrator   | BashOperator       | Airflow triggers dbt run commands.                                                                                                 |
| Authentication | Bridge Pattern     | Credentials fetched dynamically from Airflow Connections and injected into dbt as Environment Variables. No secrets stored in git. |

## 4. Next Steps

With the Transformation layer complete, the Data Platform is functionally finished (**Extract → Load → Transform**). The final phase is **Day 8: CI/CD & Automation**, where I will set up a CI pipeline (GitHub Actions) to lint SQL/Python code and verify build integrity on every Pull Request.

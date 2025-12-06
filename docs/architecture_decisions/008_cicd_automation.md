# Day 8: CI/CD & Automation Architecture

## 1. Executive Summary

The goal of Day 8 was to implement **Continuous Integration and Continuous Delivery (CI/CD)**. I established automated quality gates to ensure that no broken code reaches the production branch (**main**) and automated the artifact delivery process.

The pipeline is built on **GitHub Actions**, offering a zero-cost, fully integrated DevOps workflow.

---

## 2. Key Design Decisions

### A. CI Strategy: The "Quality Gate"

**Context:**
We need to verify code quality across three languages (Python, HCL, SQL/Jinja) before merging.

**Decision:**
Implemented a multi-stage CI pipeline running in parallel:

- **Python:** `ruff` for ultra-fast linting of Airflow DAGs
- **Terraform:** `terraform validate` to check syntax & configuration correctness
- **dbt:** `dbt parse` to validate SQL/YAML structure and Jinja references

---

### B. dbt Validation: Parse vs. Compile

**Challenge:**
Running `dbt compile` requires Snowflake connectivity, leading to security concerns (secrets in CI), cost implications, and slower pipelines.

**Decision:**
Use **dbt parse**.

**Justification:**

- **Security:** No live database connection required
- **Speed:** Completes in seconds
- **Trade-off:** Logical SQL errors (invalid columns) are caught during developer testing, not CI

---

### C. CD Strategy: Immutable Artifacts

**Context:**
Manual Airflow updates are error-prone and lead to environment drift.

**Decision:**
Implemented a **Docker Build & Push** workflow triggered on merge to `main`.

**Mechanism:**

- Build a custom Airflow image with dependencies pre-installed
- Tag with both the Git SHA (`:abc1234`) and `:latest`
- Push to Docker Hub

**Impact:**
Ensures production code is **bit-for-bit identical** to the tested code, eliminating “works on my machine” issues.

---

### D. CD Optimization: Smart Path Filtering

**Context:**
Building Docker images takes 2–3 minutes. Rebuilding when only docs or Terraform change wastes resources.

**Decision:**
Enable **path filtering** using `dorny/paths-filter`.

**Logic:**

- Docker Build & Push runs **only when `airflow/**` changes\*\*
- Docs deployment runs **on every push**

**Impact:**
Reduces CI/CD runtime by **~40%** for non-code commits.

---

### E. Documentation Automation: Embedded Lineage

**Context:**
Stakeholders need visibility into how data models connect—not just SQL files.

**Decision:**
Integrate **dbt docs generate** in the CD pipeline.

**Mechanism:**

1. CD pipeline injects Snowflake credentials securely
2. Executes `dbt docs generate`
3. Copies artifacts into `docs/dbt/` inside the MkDocs site

**Result:**
A single URL hosts:

- Architecture Decision Records (ADRs)
- End-to-end Lineage Graph
- dbt documentation

---

## 3. Pipeline Configuration

| Workflow | Trigger      | Jobs                                               | Tools                             |
| -------- | ------------ | -------------------------------------------------- | --------------------------------- |
| **CI**   | Pull Request | python-lint, terraform-validate, dbt-validate      | Ruff, Terraform CLI, dbt-core     |
| **CD**   | Push to Main | build-and-push (conditional), deploy-docs (always) | Docker Buildx, Docker Hub, MkDocs |

---

## 4. Final Project Status

With the completion of Day 8, the **Core Telecoms Data Platform** is fully automated and production-ready.

- **Infrastructure:** Provisioned & secured (Terraform)
- **Orchestration:** Containerized & scheduled (Airflow 3)
- **Data Lake:** Hydrated & partitioned (S3)
- **Warehouse:** Modeled & served (Snowflake / dbt)
- **Operations:** Automated (GitHub Actions)

---

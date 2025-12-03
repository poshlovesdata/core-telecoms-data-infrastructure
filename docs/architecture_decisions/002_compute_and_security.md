# Day 2: Compute Engine & Identity Architecture

## 1. Executive Summary

The goal of Day 2 was to provision the Data Warehouse (Compute) and establish the Identity Access Management (IAM) layer for the data pipeline. I successfully configured **Snowflake** as the central data warehouse and implemented a **Hybrid Identity Model** in AWS to support both local development (Docker) and future production deployment (EC2/ECS) without code changes.

## 2. Key Design Decisions

### A. Compute Engine: Snowflake vs. Redshift

- **Context:** The project requires a scalable SQL engine to transform data.
- **Constraint:** Current VPC (eu-north-1) does not have a NAT Gateway, making private Redshift cluster connectivity difficult.
- **Decision:** Selected Snowflake (Standard Edition) on AWS.
- **Justification:**

  - **Connectivity:** Operates as SaaS over public HTTPS, no NAT Gateway or complex VPC Endpoints required.
  - **Cost:** Leveraged 30-day Free Trial ($400 credits), avoiding Redshift costs.
  - **Separation of Compute & Storage:** Ideal for bursty batch processing pipelines.

### B. Identity Management: The "Hybrid Parity" Pattern

- **Context:** Pipeline runs locally in Docker but is designed for EC2/ECS production.
- **Challenge:** Local containers need Access Keys; production servers should use IAM Roles.
- **Decision:** Implemented "One Policy, Two Identities" pattern in Terraform.

  - **Resource 1 (Prod):** `aws_iam_role` with Trust Policy for `ec2.amazonaws.com`
  - **Resource 2 (Local):** `aws_iam_user` with programmatic Access Keys
  - **Shared Logic:** Both identities attached to the same `aws_iam_policy` (`core-telecoms-airflow-policy`).

- **Impact:** Guarantees environment parity; code working locally ensures production functionality.

### C. Secrets Management: SSM vs. Secrets Manager

- **Context:** Airflow needs to store Snowflake password and database credentials securely.
- **Decision:** Selected AWS Systems Manager (SSM) Parameter Store (Standard).
- **Justification:**

  - **Cost:** SSM Standard parameters are free; Secrets Manager costs $0.40/secret/month.
  - **Security:** `SecureString` type ensures encryption at rest.
  - **Implementation Detail:** "Lifecycle Ignore" pattern in Terraform:

    - Terraform creates resource with dummy value (`CHANGE_ME`).
    - Actual secret updated manually in Console.
    - Terraform ignores drift (`lifecycle { ignore_changes = [value] }`) preventing overwrites.

## 3. Security & Governance

- **IAM Least Privilege Scope:**

  - **S3:** `GetObject`, `PutObject`, `ListBucket` only on `cde-*-raw` and `cde-*-curated` buckets.
  - **SSM:** `GetParameter` only on paths starting with `/core_telecoms/*`.

- **Result:** Even if Airflow credentials were compromised, attackers cannot spin up EC2 instances or delete unrelated infrastructure.

## 4. Technical Trade-Off Analysis

| Feature         | Production Enterprise Approach      | Capstone (Current) Approach | Reasoning                                                            |
| --------------- | ----------------------------------- | --------------------------- | -------------------------------------------------------------------- |
| Secrets         | AWS Secrets Manager (Auto-Rotation) | SSM Parameter Store         | Saves cost; auto-rotation is overkill for a short-term capstone.     |
| Compute Network | AWS PrivateLink (VPC Endpoint)      | Public Internet (TLS 1.2)   | PrivateLink costs ~$30/month; TLS is secure enough for non-PII data. |
| Dev Auth        | AWS SSO / IAM Identity Center       | IAM User (Access Keys)      | Simplifies local Docker setup without complex SSO integration.       |

## 5. Next Steps

With the Compute engine ready and Identity secured, the next phase is **Orchestration Setup**. I will configure the local **Airflow** environment (Docker) to use the IAM User keys and connect to the Snowflake Warehouse.

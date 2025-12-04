# Day 1: Cloud Infrastructure & Foundation

## 1. Executive Summary

The goal of Day 1 was to establish a secure, reproducible, and scalable cloud foundation for the Core Telecoms data platform. I successfully provisioned a Virtual Private Cloud (VPC) in **eu-north-1 (Stockholm)** and a tiered Data Lake architecture using **Terraform** (Infrastructure as Code).

The priority was to balance **Production-Grade Security** with **Cost Optimization** for a zero-revenue capstone environment.

## 2. Key Design Decisions

### A. Infrastructure as Code (IaC) Strategy

- **Decision:** Adopted a Modular Terraform Architecture rather than a monolithic `main.tf` file.
- **Justification:** Separation of concerns. Networking (`vpc`), Storage (`s3`), and Identity (`iam`) are decoupled. Allows updates to the network without risking the state of data storage.
- **Tooling:** Implemented pre-commit hooks to enforce formatting (`terraform fmt`) and linting before code enters the repository, ensuring high code quality from Day 1.

### B. The "Zero-Cost" Network Architecture

- **Context:** A standard enterprise VPC uses NAT Gateways in private subnets to allow outbound internet access.
- **Constraint:** NAT Gateways cost ~$32/month per Availability Zone.
- **Decision:** Deployed a standard VPC (Public/Private subnets) but disabled NAT Gateways.
- **Impact:** Resources in Private Subnets are currently air-gapped from the internet.
- **Mitigation:** Compute resources requiring internet access (e.g., installing Python packages) will be placed in Public Subnets secured by strict Security Groups restricting access to specific IPs. Maintains security without the monthly cost.

### C. Modern State Management (Locking)

- **Context:** Terraform requires a lock to prevent concurrent infrastructure modifications that can corrupt the state file.
- **Decision:** Leveraged S3 Native Locking (`use_lockfile = true`) instead of the legacy DynamoDB approach.
- **Justification:** Utilizes strong consistency features released by AWS in 2024/2025, simplifying the infrastructure stack and maintaining safety.

### D. Data Lake Security (The "Iron Dome")

- **Decision:** Enforced Server-Side Encryption (SSE-S3) and Public Access Blocks on all S3 buckets.
- **Justification:** "Secure by Default." Even in a demo environment, data leaks are unacceptable.

  - `block_public_acls = true`: Prevents accidental public uploads.
  - `restrict_public_buckets = true`: Overrides any bad bucket policies.

- **Result:** Data Lake is inaccessible from the public internet, ensuring compliance with data privacy standards.

### E. FinOps: Storage Lifecycle Management

- **Context:** Data accumulates over time, increasing storage costs. Most analytics queries target recent data ("Hot"), while older data is rarely accessed ("Cold").

- **Decision:** Implemented an S3 Lifecycle Policy via Terraform.

  - Transition to Standard-IA: After 30 days (Save ~40%).

  - Transition to Glacier IR: After 90 days (Save ~80%).

  - Cleanup: Delete non-current versions (ghost files) after 7 days.

- **Justification:** Automates cost optimization without manual intervention. Ensures the platform remains cost-effective as data volume grows, aligning with enterprise FinOps best practices.

## 3. Naming Conventions & Tagging

- **Resource Pattern:** `cde-[project]-[resource]`

  - Example: `cde-core-telecoms-datalake`

- **Tagging Strategy:**

  - `ManagedBy = Terraform`: Indicates immutable infrastructure.
  - `Environment = Dev`: Allows cost allocation and automated cleanup.
  - `Owner = DataEngineering`: Identifies the responsible team.

## 4. Technical Trade-Off Analysis

| Feature     | Production Approach      | Capstone (Current) Approach     | Reasoning                                                                 |
| ----------- | ------------------------ | ------------------------------- | ------------------------------------------------------------------------- |
| Network     | Multi-AZ NAT Gateways    | No NAT Gateway                  | Saves ~$64/month. Complexity handled via Security Groups.                 |
| Storage     | `force_destroy = false`  | `force_destroy = true`          | Allows rapid iteration/teardown during development.                       |
| Environment | Multi-Account (Dev/Prod) | Single Account (Variable-based) | Reduces overhead of managing multiple AWS accounts for a single engineer. |

## 5. Next Steps

With the foundation secured, the immediate next phase is **Compute Provisioning**. I will deploy **Snowflake** (via Free Trial) as the Data Warehouse to leverage its separation of storage and compute, bypassing networking complexities of Redshift in a NAT-less environment.

# Snowflake Password
# This a placeholder. The value must be updatde manually in AWS Console.
resource "aws_ssm_parameter" "snowflake_password" {
  name        = "/core_telecoms/snowflake/password"
  description = "Password for Snowflake Airflow user"
  type        = "SecureString"
  value       = "CHANGE_ME_IN_CONSOLE"

  # To prevent Terraform from overwriting the updated password
  lifecycle {
    ignore_changes = [value]
  }
}

# Snowflake account ID/URL
resource "aws_ssm_parameter" "snowflake_account" {
  name        = "/core_telecoms/snowflake/account"
  description = "Snowflake Account ID"
  type        = "SecureString"
  value       = "CHANGE_ME_IN_CONSOLE"

  lifecycle {
    ignore_changes = [value]
  }
}

# Snowflake Warehouse
resource "aws_ssm_parameter" "snowflake_warehouse" {
  name  = "/core_telecoms/snowflake/warehouse"
  type  = "String"
  value = "core_telecom_warehouse"
}

# Snowflake Database
resource "aws_ssm_parameter" "snowflake_database" {
  name  = "/core_telecoms/snowflake/database"
  type  = "String"
  value = "core_telecom"
}

# Snowflake Role
resource "aws_ssm_parameter" "snowflake_role" {
  name  = "/core_telecoms/snowflake/role"
  type  = "String"
  value = "core_data_engineering"
}

# Postgres Password (Source DB)
resource "aws_ssm_parameter" "postgres_password" {
  name        = "/core_telecoms/postgres/postgres_password"
  description = "Password for the upstream Source Postgres DB"
  type        = "SecureString"
  value       = "CHANGE_ME_IN_CONSOLE"

  lifecycle {
    ignore_changes = [value]
  }
}

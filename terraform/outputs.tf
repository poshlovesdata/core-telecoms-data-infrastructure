output "airflow_iam_access_key_id" {
  description = "Airflow Access key for Local Dev"
  value       = aws_iam_access_key.airflow_local_key.id
  sensitive   = true
}

output "airflow_iam_access_secret_key" {
  description = "Airflow Secret key for Local Dev"
  value       = aws_iam_access_key.airflow_local_key.secret
  sensitive   = true
}

output "snowflake_role_arn" {
  description = "ARN of the Snowflake Access Role (Use this in CREATE STORAGE INTEGRATION)"
  value       = aws_iam_role.snowflake_s3_role.arn
}

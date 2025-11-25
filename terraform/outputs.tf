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

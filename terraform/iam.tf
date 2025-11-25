resource "aws_iam_policy" "airflow_policy" {
  name        = "core-telecoms-airflow-policy"
  description = "Permissions for Airflow to access S3 and SSM"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      # Access to Data Lake Buckets (Raw & Curated)
      {
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:ListBucket"
        ]
        Effect = "Allow"
        Resource = [
          "arn:aws:s3:::${local.common_prefix}-raw",
          "arn:aws:s3:::${local.common_prefix}-raw/*",
          "arn:aws:s3:::${local.common_prefix}-curated",
          "arn:aws:s3:::${local.common_prefix}-curated/*",
        ]
      },
      # Access to SSM Parameters
      {
        Action = [
          "ssm:GetParameter",
          "ssm:GetParameters"
        ]
        Effect   = "Allow"
        Resource = "arn:aws:ssm:${var.aws_region}:*:parameter/core_telecoms/*"
      }

    ]
  })
}

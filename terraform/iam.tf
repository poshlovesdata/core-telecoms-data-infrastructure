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

# Production Identity
# To be used if airflow gets deployed to production (EC2)
data "aws_iam_policy_document" "airflow_ec2_trust" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "airflow_execution_role" {
  name = "airflow_execution_role"

  assume_role_policy = data.aws_iam_policy_document.airflow_ec2_trust.json

  tags = {
    Purpose = "Airflow Production Execution"
    Owner   = "DataEngineering"
  }
}

# Attach Policy to role
resource "aws_iam_role_policy_attachment" "role_attach" {
  role       = aws_iam_role.airflow_execution_role.name
  policy_arn = aws_iam_policy.airflow_policy.arn
}

# Local Airflow Identity
# To be used for local airflow development
resource "aws_iam_user" "airflow_local_user" {
  name = "airflow_local_dev"

  tags = {
    Purpose = "Local Development"
  }
}

resource "aws_iam_user_policy_attachment" "user_attach" {
  user       = aws_iam_user.airflow_local_user.name
  policy_arn = aws_iam_policy.airflow_policy.arn
}


resource "aws_iam_access_key" "airflow_local_key" {
  user = aws_iam_user.airflow_local_user.name
}

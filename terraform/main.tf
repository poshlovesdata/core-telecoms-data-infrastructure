module "vpc" {
  source = "terraform-aws-modules/vpc/aws"

  name = "core-telecoms-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["eu-north-1a", "eu-north-1b"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24"]

  enable_nat_gateway = false
  single_nat_gateway = false
  enable_vpn_gateway = false

  tags = {
    Environment = var.environment
  }
}


locals {
  common_prefix = "${var.project_name}-${var.environment}"
  bucket_name   = "cde-${var.project_name}-data-lake"
  common_tags = {
    Project            = var.project_name
    Environment        = var.environment
    ManagedByTerraform = true
  }
}

# S3 buckets for storage
# This bucket hosts both 'raw/' and 'curated/' prefixes
resource "aws_s3_bucket" "data_lake" {
  bucket        = local.bucket_name
  force_destroy = false

  tags = merge(local.common_tags, { Layer = "DataLake" })
}

resource "aws_s3_bucket_versioning" "lake_versioning" {
  bucket = aws_s3_bucket.data_lake.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "lake_encryption" {
  bucket = aws_s3_bucket.data_lake.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "lake_block" {
  bucket = aws_s3_bucket.data_lake.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

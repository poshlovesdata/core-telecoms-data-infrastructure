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
  common_tags = {
    Project            = var.project_name
    Environment        = var.environment
    ManagedByTerraform = true
  }
}

# S3 buckets for storage
resource "aws_s3_bucket" "raw_layer" {
  bucket = "${local.common_prefix}-raw"

  tags = merge(local.common_tags, { Layer = "Raw" })
}

resource "aws_s3_bucket_versioning" "raw_versioning" {
  bucket = aws_s3_bucket.raw_layer.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "raw_encryption" {
  bucket = aws_s3_bucket.raw_layer.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "raw_block" {
  bucket = aws_s3_bucket.raw_layer.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Curated layer
resource "aws_s3_bucket" "curated_layer" {
  bucket = "${local.common_prefix}-curated"

  tags = merge(local.common_tags, { Layer = "Curated" })
}

resource "aws_s3_bucket_versioning" "curated_versioning" {
  bucket = aws_s3_bucket.curated_layer.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "curated_encryption" {
  bucket = aws_s3_bucket.curated_layer.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "curated_block" {
  bucket = aws_s3_bucket.curated_layer.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

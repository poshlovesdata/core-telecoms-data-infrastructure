terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}

terraform {
  backend "s3" {
    bucket       = "core-telecoms-terraform-state"
    key          = "core-telecoms/dev/terraform.tfstate"
    region       = "eu-north-1"
    encrypt      = true
    use_lockfile = true
  }
}

# Configure the AWS Provider
provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project            = var.project_name
      Environment        = var.environment
      ManagedByTerraform = true
      Owner              = "data_engineering_team"
    }
  }

}

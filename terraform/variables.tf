variable "aws_region" {
  description = "The AWS region to deploy resources in"
  type        = string
  default     = "eu-north-1"
}

variable "project_name" {
  description = "The name of the project"
  type        = string
  default     = "core-telecoms"
}

variable "environment" {
  description = "The deployment environment"
  type        = string
  default     = "dev"

}

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

variable "snowflake_account_arn" {
  description = "STORAGE_AWS_IAM_USER_ARN from Snowflake DESC INTEGRATION"
  type        = string
  default     = "arn:aws:iam::714551764970:user/rso71000-s" # Placeholder beofre getting real values

}

variable "snowflake_external_id" {
  description = "STORAGE_AWS_EXTERNAL_ID from Snowflake DESC INTEGRATION"
  type        = string
  default     = "VN34785_SFCRole=4_p17yMlVg46U8LmqKfS/vgyj7KhA=" # Placeholder beofre getting real values

}

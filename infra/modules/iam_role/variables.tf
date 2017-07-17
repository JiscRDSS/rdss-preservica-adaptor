variable "project" {
  description = "Project name."
}

variable "environment" {
  description = "Environment we are working with."
}

variable "input_stream_arn" {
  description = "Input stream ARN."
}

variable "error_stream_arn" {
  description = "Error stream ARN."
}

variable "upload_bucket_arn" {
  description = "Upload bucket ARN."
}

variable "dynamodb_arn" {
  description = "Dynamodb to keep kinesis stream read ARN."
  default     = "*"
}

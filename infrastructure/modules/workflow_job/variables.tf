variable "name" {
  description = "The name of the Cloud Run Job"
  type        = string
}

variable "region" {
  description = "The region where resources will be deployed"
  type        = string
}



variable "docker_image_url" {
  description = "The Docker image URL for the job"
  type        = string
}

variable "workflow_name" {
  description = "The WORKFLOW_NAME environment variable"
  type        = string
}

variable "secrets" {
  description = "A map of secrets to be used in the job"
  type        = map(string)
  default     = {}
}

variable "additional_env_vars" {
  description = "Additional environment variables"
  type        = map(string)
  default     = {}
}

variable "project_id" {
  description = "The GCP project ID"
  type        = string
}


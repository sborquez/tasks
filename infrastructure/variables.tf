variable "project_id" {
  description = "The GCP project ID"
  type        = string
}

variable "region" {
  description = "The GCP region"
  type        = string
  default     = "us-central1"
}

variable "placeholder_docker_image_url" {
  description = "The URL of the Docker image for Cloud Run Jobs, including the tag/version"
  type        = string
  default     = "gcr.io/google-containers/busybox"
}

variable "pubsub_topic_name" {
  description = "The name of the Pub/Sub topic for triggering workflows"
  type        = string
  default     = "workflow-trigger-topic"
}

variable "trigger_cloud_function_name" {
  description = "The name of the Cloud Function to listen to Pub/Sub and trigger Cloud Run Jobs"
  type        = string
  default     = "workflow-trigger-function"
}

variable "hello_world_job_name" {
  description = "The name of the Cloud Run Job for the hello_world workflow"
  type        = string
  default     = "hello-world-job"
}

variable "push_feature_job_name" {
  description = "The name of the Cloud Run Job for the push_feature workflow"
  type        = string
  default     = "push-feature-job"
}

// Secret Manager Variables
variable "git_token_value" {
  description = "A git access token to be stored in Secret Manager"
  type        = string
  sensitive = true
}

variable "anthropic_api_key_value" {
  description = "An API key for the Anthropics API to be stored in Secret Manager"
  type        = string
  sensitive = true
}

variable "openai_api_key_value" {
  description = "An API key for the OpenAI API to be stored in Secret Manager"
  type        = string
  sensitive = true
}
// Other variables
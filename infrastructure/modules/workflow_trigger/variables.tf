variable "project_id" {
  description = "The GCP project ID"
  type        = string
}

variable "region" {
  description = "The GCP region"
  type        = string
}

variable "pubsub_topic_name" {
  description = "The name of the Pub/Sub topic for triggering workflows"
  type        = string
}

variable "trigger_cloud_function_name" {
  description = "The name of the Cloud Function to listen to Pub/Sub and trigger Cloud Run Jobs"
  type        = string
}

variable "source_archive_path" {
  description = "Path to the Cloud Function source code archive"
  type        = string
}

variable "job_names" {
  description = "A map of workflow identifiers to their Cloud Run Job names"
  type        = map(string)
}
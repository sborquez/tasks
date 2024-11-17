variable "project_id" {
  description = "The GCP project ID"
  type        = string
}

variable "region" {
  description = "The GCP region"
  type        = string
}

variable "publisher_cloud_function_name" {
  description = "The name of the Cloud Function to publish a trigger message via HTTP"
  type        = string
}

variable "source_archive_path" {
  description = "Path to the Cloud Function source code archive"
  type        = string
}

variable "pubsub_topic_name" {
  description = "The name of the Pub/Sub topic for triggering workflows"
  type        = string
  default     = "workflow-trigger-topic"
}

variable "target_workflow" {
  description = "The name of the workflow to trigger"
  type        = string
}
# Add project_id and region

output "project_id" {
  description = "The GCP project ID"
  value       = var.project_id
}

output "region" {
  description = "The GCP region"
  value       = var.region
}

output "pubsub_topic_name" {
  description = "The name of the Pub/Sub topic for triggering workflows"
  value       = google_pubsub_topic.workflow_trigger_topic.name
}

output "cloud_function_url" {
  description = "The URL of the Cloud Function that listens to Pub/Sub and triggers Cloud Run Jobs"
  value       = google_cloudfunctions_function.workflow_trigger_function.https_trigger_url
}

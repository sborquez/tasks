output "workflow_trigger_topic_name" {
  description = "The name of the Pub/Sub topic for triggering workflows"
  value       = google_pubsub_topic.workflow_trigger_topic.name
}

output "workflow_trigger_function_name" {
  description = "The name of the Cloud Function that triggers workflows"
  value       = google_cloudfunctions_function.workflow_trigger_function.name
}

output "workflow_trigger_function_service_account_email" {
  description = "The service account email of the Cloud Function"
  value       = google_cloudfunctions_function.workflow_trigger_function.service_account_email
}
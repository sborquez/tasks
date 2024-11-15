# Add project_id and region

output "project_id" {
  description = "The GCP project ID"
  value       = var.project_id
}

output "region" {
  description = "The GCP region"
  value       = var.region
}

output "workflow_trigger_topic_name" {
  description = "The name of the Pub/Sub topic for triggering workflows"
  value       = module.workflow_trigger.workflow_trigger_topic_name
}

output "workflow_trigger_function_name" {
  description = "The name of the Cloud Function that triggers workflows"
  value       = module.workflow_trigger.workflow_trigger_function_name
}

output "workflow_trigger_function_service_account_email" {
  description = "The service account email of the Cloud Function"
  value       = module.workflow_trigger.workflow_trigger_function_service_account_email
}

# output "cloud_function_url_push_feature" {
#   description = "The URL of the Cloud Function that triggers the push_feature workflow via HTTP"
#   value       = google_cloudfunctions_function.push_feature_function.https_trigger_url
# }

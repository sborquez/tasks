output "publisher_cloud_function_name" {
  description = "The name of the Cloud Function to publish a trigger message via HTTP"
  value       = google_cloudfunctions_function.publisher_cloud_function.name
}

output "publisher_cloud_function_url" {
  description = "The URL of the Cloud Function to publish a trigger message via HTTP"
  value       = google_cloudfunctions_function.publisher_cloud_function.https_trigger_url
}
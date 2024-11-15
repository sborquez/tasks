# Convert the job_names map to environment variables
locals {
  job_env_vars = { for key, value in var.job_names : "${upper(key)}_JOB_NAME" => value }
}

# Pub/Sub topic for triggering workflows cloud function
resource "google_pubsub_topic" "workflow_trigger_topic" {
  name    = var.pubsub_topic_name
  project = var.project_id
}
# Cloud Function to listen to Pub/Sub and trigger Cloud Run Jobs
resource "google_storage_bucket" "workflow_trigger_bucket" {
  name     = "${var.project_id}-${var.trigger_cloud_function_name}-bucket"
  location = var.region
}

resource "google_storage_bucket_object" "workflow_trigger_archive" {
  name   = "${var.trigger_cloud_function_name}-source.zip"
  bucket = google_storage_bucket.workflow_trigger_bucket.name
  source = var.source_archive_path
  depends_on = [google_storage_bucket.workflow_trigger_bucket]
}

resource "google_cloudfunctions_function" "workflow_trigger_function" {
  name        = var.trigger_cloud_function_name
  description = "Trigger Cloud Run Jobs from Pub/Sub"
  runtime     = "python312"

  available_memory_mb   = 256
  source_archive_bucket = google_storage_bucket.workflow_trigger_bucket.name
  source_archive_object = google_storage_bucket_object.workflow_trigger_archive.name
  entry_point           = "workflow_trigger"

  environment_variables = local.job_env_vars

  event_trigger {
    event_type = "google.pubsub.topic.publish"
    resource   = google_pubsub_topic.workflow_trigger_topic.id
  }

  depends_on = [
    google_storage_bucket_object.workflow_trigger_archive,
    google_pubsub_topic.workflow_trigger_topic,
  ]
}
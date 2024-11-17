resource "google_storage_bucket" "publisher_cloud_function_bucket" {
  name     = "${var.project_id}-${var.publisher_cloud_function_name}-bucket"
  location = var.region
}

resource "google_storage_bucket_object" "publisher_cloud_function_archive" {
  name   = "${var.publisher_cloud_function_name}-source.zip"
  bucket = google_storage_bucket.publisher_cloud_function_bucket.name
  source = var.source_archive_path
  depends_on = [ google_storage_bucket.publisher_cloud_function_bucket ]
}

resource "google_cloudfunctions_function" "publisher_cloud_function" {
  name        = var.publisher_cloud_function_name
  description = "Publish a message to Pub/Sub to trigger the a workflow"
  runtime     = "python312"

  available_memory_mb   = 256
  source_archive_bucket = google_storage_bucket.publisher_cloud_function_bucket.name
  source_archive_object = google_storage_bucket_object.publisher_cloud_function_archive.name
  entry_point           = "publish"
  trigger_http = true

  environment_variables = {
    PUBSUB_TOPIC = var.pubsub_topic_name
    TARGET_WORKFLOW = var.target_workflow
    GCP_PROJECT = var.project_id
  }

  depends_on = [
    google_storage_bucket_object.publisher_cloud_function_archive,
  ]
}

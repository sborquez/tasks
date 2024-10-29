provider "google" {
  project = var.project_id
  region  = var.region
}

data "google_project" "current" {
  project_id = var.project_id
}

# Enable necessary APIs
resource "google_project_service" "cloud_run" {
  project = data.google_project.current.project_id
  service = "run.googleapis.com"
}

resource "google_project_service" "cloud_build" {
  project = data.google_project.current.project_id
  service = "cloudbuild.googleapis.com"
}

resource "google_project_service" "container_registry" {
  project = data.google_project.current.project_id
  service = "containerregistry.googleapis.com"
}

resource "google_project_service" "cloud_functions" {
  project = data.google_project.current.project_id
  service = "cloudfunctions.googleapis.com"
}

resource "google_project_service" "pubsub" {
  project = data.google_project.current.project_id
  service = "pubsub.googleapis.com"
}

resource "google_project_service" "secretmanager" {
  project = data.google_project.current.project_id
  service = "secretmanager.googleapis.com"
}

# Pub/Sub topic for triggering workflows cloud function
resource "google_pubsub_topic" "workflow_trigger_topic" {
  name    = var.pubsub_topic_name
  project = data.google_project.current.project_id
}

# Cloud Function to listen to Pub/Sub and trigger Cloud Run Jobs
resource "google_storage_bucket" "workflow_trigger_bucket" {
  name     = "${var.project_id}-${var.cloud_function_name}-bucket"
  location = var.region
}

resource "google_storage_bucket_object" "workflow_trigger_archive" {
  name   = "${var.cloud_function_name}-source.zip"
  bucket = google_storage_bucket.workflow_trigger_bucket.name
  source = "./${var.cloud_function_name}-source.zip"  # Ensure this path is correct
}

resource "google_cloudfunctions_function" "workflow_trigger_function" {
  name        = var.cloud_function_name
  description = "Trigger Cloud Run Jobs from Pub/Sub"
  runtime     = "python312"

  available_memory_mb   = 256
  source_archive_bucket = google_storage_bucket.workflow_trigger_bucket.name
  source_archive_object = google_storage_bucket_object.workflow_trigger_archive.name
  entry_point           = "workflow_trigger"

  // TODO: Move the job names to a firestore database
  environment_variables = {
    HELLO_WORLD_JOB_NAME = var.hello_world_job_name
  }

  event_trigger {
    event_type = "google.pubsub.topic.publish"
    resource   = google_pubsub_topic.workflow_trigger_topic.id
  }

  depends_on = [
    google_storage_bucket_object.workflow_trigger_archive,
    google_pubsub_topic.workflow_trigger_topic,

  ]
}


# Cloud Run Job for hello_world workflow
resource "google_cloud_run_v2_job" "hello_world_job" {
  name     = var.hello_world_job_name
  location = var.region

  depends_on = [ google_secret_manager_secret.git_token, google_secret_manager_secret_version.git_token ]

  template {
    template {
      containers {
        image = var.placeholder_docker_image_url

        # Environment variable for WORKFLOW_NAME
        env {
          name  = "WORKFLOW_NAME"
          value = "hello_world"
        }
        # Environment variable for GIT_TOKEN from Secret Manager
        env {
          name = "GIT_TOKEN"

          value_source {
            secret_key_ref {
              secret = google_secret_manager_secret.git_token.secret_id
              version = "latest"
            }
          }
        }
      }
    }
  }
}

# Access GIT_TOKEN from Secret Manager
resource "google_secret_manager_secret" "git_token" {
  secret_id = "git-access-token"
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "git_token" {
  secret      = google_secret_manager_secret.git_token.id
  secret_data = var.git_token_value  # Using the input variable here
  depends_on  = [google_secret_manager_secret.git_token]
}

resource "google_secret_manager_secret_iam_member" "git_token_access" {
  secret_id = google_secret_manager_secret.git_token.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${data.google_project.current.number}-compute@developer.gserviceaccount.com"
  depends_on = [google_secret_manager_secret.git_token]
}

# IAM permissions for Cloud Function to trigger Cloud Run Jobs
resource "google_project_iam_member" "cloud_run_invoker" {
  project = data.google_project.current.project_id
  role    = "roles/run.invoker"
  member  = "serviceAccount:${google_cloudfunctions_function.workflow_trigger_function.service_account_email}"
}
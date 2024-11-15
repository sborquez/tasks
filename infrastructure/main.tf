provider "google" {
  project = var.project_id
  region  = var.region
}

data "google_project" "current" {
  project_id = var.project_id
}

# Enable necessary APIs
locals {
  required_apis = [
    "run.googleapis.com",
    "cloudbuild.googleapis.com",
    "containerregistry.googleapis.com",
    "cloudfunctions.googleapis.com",
    "pubsub.googleapis.com",
    "secretmanager.googleapis.com",
  ]
}

resource "google_project_service" "project_services" {
  for_each = toset(local.required_apis)
  project = data.google_project.current.project_id
  service = each.key
  disable_on_destroy = false
}

resource "time_sleep" "wait_for_api_activation" {
  depends_on = [google_project_service.project_services]
  create_duration = "60s"
}

module "workflow_trigger" {
  source = "./modules/workflow_trigger"

  project_id                  = var.project_id
  region                      = var.region
  pubsub_topic_name           = var.pubsub_topic_name
  trigger_cloud_function_name = var.trigger_cloud_function_name
  source_archive_path         = "./${var.trigger_cloud_function_name}-source.zip"
  job_names                   = {
    hello_world  = var.hello_world_job_name
    push_feature = var.push_feature_job_name
  }

  depends_on = [
    google_project_service.project_services,
    time_sleep.wait_for_api_activation,
  ]
}

# Cloud Function to listen to HTTP and send a Pub/Sub message
# resource "google_storage_bucket" "push_feature_cloud_function_bucket" {
#   name     = "${var.project_id}-${var.push_feature_cloud_function_name}-bucket"
#   location = var.region
# }

# resource "google_storage_bucket_object" "push_feature_cloud_function_archive" {
#   name   = "${var.push_feature_cloud_function_name}-source.zip"
#   bucket = google_storage_bucket.push_feature_cloud_function_bucket.name
#   source = "./${var.push_feature_cloud_function_name}-source.zip"
#   depends_on = [ google_storage_bucket.push_feature_cloud_function_bucket ]
# }

# resource "google_cloudfunctions_function" "push_feature_function" {
#   name        = var.push_feature_cloud_function_name
#   description = "Publish a message to Pub/Sub to trigger the push_feature workflow"
#   runtime     = "python312"

#   available_memory_mb   = 256
#   source_archive_bucket = google_storage_bucket.push_feature_cloud_function_bucket.name
#   source_archive_object = google_storage_bucket_object.push_feature_cloud_function_archive.name
#   entry_point           = "push_feature_request"
#   trigger_http = true

#   environment_variables = {
#     PUBSUB_TOPIC = var.pubsub_topic_name
#   }

#   depends_on = [
#     google_storage_bucket_object.push_feature_cloud_function_archive,
#     google_pubsub_topic.workflow_trigger_topic,
#   ]
# }


# Cloud Run Job
## hello_world workflow
module "hello_world_job" {
  source = "./modules/workflow_job"

  name             = var.hello_world_job_name
  region           = var.region
  docker_image_url = var.placeholder_docker_image_url
  workflow_name    = "hello_world"
  project_id       = var.project_id

  secrets = {
    GIT_TOKEN = google_secret_manager_secret.git_token.secret_id
  }

  depends_on = [
    google_secret_manager_secret.git_token,
    google_secret_manager_secret_version.git_token,
  ]
}

## push_feature workflow
module "push_feature_job" {
  source = "./modules/workflow_job"

  name             = var.push_feature_job_name
  region           = var.region
  docker_image_url = var.placeholder_docker_image_url
  workflow_name    = "push_feature"
  project_id       = var.project_id

  secrets = {
    GIT_TOKEN           = google_secret_manager_secret.git_token.secret_id
    ANTHROPIC_API_KEY   = google_secret_manager_secret.anthropic_api_key.secret_id
  }

  depends_on = [
    google_secret_manager_secret.git_token,
    google_secret_manager_secret_version.git_token,
    google_secret_manager_secret.anthropic_api_key,
    google_secret_manager_secret_version.anthropic_api_key,
  ]
}


# Access GIT_TOKEN from Secret Manager
resource "google_secret_manager_secret" "git_token" {
  secret_id = "git-access-token"
  replication {
    auto {}
  }

  depends_on = [
    google_project_service.project_services,
    time_sleep.wait_for_api_activation,
  ]
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

# Anthropic API Key
resource "google_secret_manager_secret" "anthropic_api_key" {
  secret_id = "anthropic-api-key"
  replication {
    auto {}
  }

  depends_on = [
    google_project_service.project_services,
    time_sleep.wait_for_api_activation,
  ]
}

resource "google_secret_manager_secret_version" "anthropic_api_key" {
  secret      = google_secret_manager_secret.anthropic_api_key.id
  secret_data = var.anthropic_api_key_value
  depends_on  = [google_secret_manager_secret.anthropic_api_key]
}

resource "google_secret_manager_secret_iam_member" "anthropic_api_key_access" {
  secret_id = google_secret_manager_secret.anthropic_api_key.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${data.google_project.current.number}-compute@developer.gserviceaccount.com"
  depends_on = [google_secret_manager_secret.anthropic_api_key]
}

# IAM permissions for Cloud Function to trigger Cloud Run Jobs
resource "google_project_iam_member" "cloud_run_invoker" {
  project = data.google_project.current.project_id
  role    = "roles/run.invoker"
  member  = "serviceAccount:${module.workflow_trigger.workflow_trigger_function_service_account_email}"
}

# # IAM permissions for Cloud Function to send Pub/Sub messages
# resource "google_project_iam_member" "pubsub_publisher" {
#   project = data.google_project.current.project_id
#   role    = "roles/pubsub.publisher"
#   member  = "serviceAccount:${module.workflow_trigger.workflow_trigger_function_service_account_email}"
# }
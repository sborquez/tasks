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
    "secretmanager.googleapis.com",
    "firestore.googleapis.com",
  ]
}

resource "google_project_service" "project_services" {
  for_each = toset(local.required_apis)
  project = data.google_project.current.project_id
  service = each.key
  disable_on_destroy = false
}

# Service Account
## Create a service account for tasks jobs
resource "google_service_account" "tasks_jobs_service_account" {
  account_id   = "tasks-jobs-sa"
  display_name = "Tasks Jobs Service Account"
  project      = var.project_id

  depends_on = [
    google_project_service.project_services
  ]
}


## Create a service account for tasks API server
resource "google_service_account" "tasks_api_service_account" {
  account_id   = "tasks-api-sa"
  display_name = "Tasks API Service Account"
  project      = var.project_id

  depends_on = [
    google_project_service.project_services
  ]
}


# Tasks Cloud Run Jobs
## Artifact Registry Repository
resource "google_artifact_registry_repository" "tasks_repository" {
  repository_id = "tasks-images"
  format        = "DOCKER"
  location      = var.region
  description   = "Docker repository for tasks Cloud Run Jobs container images"

  labels = {
    "app" = "tasks"
  }

  depends_on = [ google_project_service.project_services ]
}

## Bucket for Cloud Run Jobs Results
resource "google_storage_bucket" "tasks_results_bucket" {
  name     = "${var.project_id}-tasks-results-bucket"
  location = var.region
}

resource "google_storage_bucket_iam_member" "tasks_bucket_access" {
  bucket = google_storage_bucket.tasks_results_bucket.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.tasks_jobs_service_account.email}"
}

resource "google_storage_bucket_object" "default_folder" {
  name   = "default/"
  content = "Default folder for results of tasks."
  bucket = google_storage_bucket.tasks_results_bucket.name

  depends_on = [google_storage_bucket.tasks_results_bucket]
}

# Firestore Database
resource "google_firestore_database" "tasks_firestore_db" {
  project     = data.google_project.current.project_id
  name        = "(default)"
  location_id = var.region
  type        = "FIRESTORE_NATIVE"

  depends_on = [google_project_service.project_services]
}


locals {
  collections = [
    "users",
    "tasks",
    "jobs",
  ]
}
resource "google_firestore_document" "tasks_firestore_db_collections" {
  project     = data.google_project.current.project_id
  database    = google_firestore_database.tasks_firestore_db.name
  for_each    = toset(local.collections)
  collection  = each.key
  document_id = "dummy"

  fields = "{}"

  depends_on = [google_firestore_database.tasks_firestore_db]
}

resource "google_project_iam_binding" "tasks_firestore_db_access" {
  project = data.google_project.current.project_id
  role    = "roles/datastore.user"
  members = [
    "serviceAccount:${google_service_account.tasks_jobs_service_account.email}",
    "serviceAccount:${google_service_account.tasks_api_service_account.email}",
  ]
}

# Cloud Jobs Launcher
resource "google_project_iam_binding" "tasks_jobs_service_account_access" {
  project = data.google_project.current.project_id
  role    = "roles/run.developer"
  members = [
    "serviceAccount:${google_service_account.tasks_api_service_account.email}",
  ]
}

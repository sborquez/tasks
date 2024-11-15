resource "google_cloud_run_v2_job" "job" {
  name     = var.name
  location = var.region

  template {
    template {
      containers {
        image = var.docker_image_url

        env {
          name  = "WORKFLOW_NAME"
          value = var.workflow_name
        }

        # Additional environment variables
        dynamic "env" {
          for_each = var.additional_env_vars
          content {
            name  = env.key
            value = env.value
          }
        }

        # Secrets as environment variables
        dynamic "env" {
          for_each = var.secrets
          content {
            name = env.key

            value_source {
              secret_key_ref {
                secret  = env.value
                version = "latest"
              }
            }
          }
        }
      }
    }
  }
}
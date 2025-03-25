# Workflows Infrastructure

This project uses Terraform to automate the setup of Google Cloud Platform (GCP) resources, including service accounts and necessary permissions for Cloud Run and Cloud Build.

## Table of Contents

- [Workflows Infrastructure](#workflows-infrastructure)
  - [Table of Contents](#table-of-contents)
  - [Prerequisites](#prerequisites)
  - [Setup Instructions](#setup-instructions)
    - [0. Granting Permissions for applying the Terraform Configuration](#0-granting-permissions-for-applying-the-terraform-configuration)
      - [GCP Permissions](#gcp-permissions)
      - [Secrets Needed](#secrets-needed)
    - [1. Initialize Terraform](#1-initialize-terraform)
    - [2. Review the Terraform Plan](#2-review-the-terraform-plan)
    - [3. Apply the Terraform Configuration](#3-apply-the-terraform-configuration)
      - [Variables](#variables)
  - [Deploying New Workflows Versions](#deploying-new-workflows-versions)


## Prerequisites

1. **Terraform**: Latest version of Terraform installed on your local machine. You can download it from [here](https://www.terraform.io/downloads.html).
2. **Google Cloud SDK**: Ensure you have the Google Cloud SDK installed and configured with the appropriate credentials. You can download it from [here](https://cloud.google.com/sdk/docs/install).
3. **Terraform Variables**: Running the following commands will set the necessary environment variables for the Terraform configuration.
    ```bash
    # Google Cloud Project ID
    export PROJECT_ID="..."

    # Your email address (has permissions on the project)
    export EMAIL="..."

    # Secrets Variables
    export GIT_TOKEN="..."
    export ANTHROPIC_API_KEY="..."
    # export OPENAI_API_KEY="..."
    # export OPENAI_API_SECRET="..."
    # export
    ```

---

## Setup Instructions

The Terraform configuration creates the following resources in your GCP project:

| **Section**                    | **Details**                                                                                                                                            |
|--------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------|
| **// APIs Enabled**            |  |
| **Cloud Run API** (`run.googleapis.com`) | Required for deploying and managing applications in Cloud Run.                                           |
| **Cloud Build API** (`cloudbuild.googleapis.com`) | Required for using Google Cloud Build to automate the build and deployment process.               |
| **Container Registry API** (`containerregistry.googleapis.com`) |  Required for storing Docker images in Google Container Registry.                   |
| **Cloud Functions API** (`cloudfunctions.googleapis.com`) | Required for deploying and managing Cloud Functions.                                      |
| **Cloud Pub/Sub API** (`pubsub.googleapis.com`) | Required for using Google Cloud Pub/Sub to publish and subscribe to messages.                     |
| **Secret Manager API** (`secretmanager.googleapis.com`) | Required for storing and managing secrets in Google Secret Manager.                       |
| **// Permissions and Service Accounts** |  |
| **Cloud Run invoker role** |  A custom role that allows users to invoke Cloud Run services. Given to the trigger Cloud Function service account. |
| **// Pub/Sub Topic and Subscription**    |  |
| **Pub/Sub Topic** | A Pub/Sub topic that triggers the Cloud Function when a message is published to the topic.                                  |
| **Pub/Sub Subscription** | A Pub/Sub subscription that listens to the Pub/Sub topic and triggers the Cloud Function.                                  |
| **Cloud Function** | A Cloud Function that is triggered by messages published to the Pub/Sub topic to run the workflows.                             |
| **// Cloud Run Jobs**             |  |
| **Workflow Jobs** | Cloud Run Jobs for each workflow implemented in the project. The initial docker image is a placeholder and can be replaced with `make deploy-jobs`. (see `variables.tf` for the default value) |
|                                | - `hello-world-job`: A Cloud Run Job that runs the `hello_world` workflow.                                                                            |
|                                | - (Add more jobs as needed for other workflows)                                                                                                       |
| **// Secrets**                 |  |
| **Secret Manager** | Secrets that are used in the Jobs for authentication and other purposes.                                                       |
### 0. Granting Permissions for applying the Terraform Configuration


#### GCP Permissions

Your account must have the necessary permissions to create resources in the GCP project. You can use the `Owner` role or have the following permissions:


```bash
if [ -z "$PROJECT_ID" ]; then
    echo "Please set the PROJECT_ID environment variable"
    exit 1
fi
if [ -z "$EMAIL" ]; then
    echo "Please set the EMAIL environment variable"
    exit 1
fi
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="user:$EMAIL" \
    --role="roles/serviceusage.serviceUsageAdmin"
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="user:$EMAIL" \
    --role="roles/iam.serviceAccountAdmin"
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="user:$EMAIL" \
  --role="roles/secretmanager.admin"
```

note: Enable the billing for the project before running the above commands.

#### Secrets Needed

You will also need some API keys for different resources:

* **GitHub Fine-grained Access Token**: You can generate a GitHub token with fine-grained access to specific repositories. This token is used to clone private repositories in the Cloud Run Jobs. You can generate a token by following the instructions [here](https://docs.github.com/en/github/authenticating-to-github/keeping-your-account-and-data-secure/creating-a-personal-access-token). The needed scores are: `Contents`, `Issues`, and `Pull Requests`.

### 1. Initialize Terraform

Navigate to the `infrastructure` directory and initialize Terraform:

```
cd infrastructure
terraform init
```

This command will download the necessary provider plugins and prepare your working directory for Terraform operations.

### 2. Review the Terraform Plan

Before applying the configuration, you can review what changes will be made to your GCP project by running:

```
terraform plan -var="project_id=$PROJECT_ID"
```


### 3. Apply the Terraform Configuration

To create the resources defined in the Terraform configuration, apply the configuration:


```
terraform apply \
  -var="project_id=$PROJECT_ID" \
  -auto-approve
```

Terraform will create the necessary resources in your GCP project. The `-auto-approve` flag is used to automatically approve the plan without requiring user confirmation.

#### Variables

The complete list of variables can be found in the `variables.tf` file. You can pass these variables to the `terraform apply` command using the `-var` flag.

| **Variable**                  | **Description**                                                                         | **Type** | **Default**                             |
|-------------------------------|-----------------------------------------------------------------------------------------|----------|-----------------------------------------|
| `placeholder_docker_image_url` | The URL of the Docker image for Cloud Run Jobs, including the tag/version               | string   | `gcr.io/google-containers/busybox`      |
| `pubsub_topic_name`           | The name of the Pub/Sub topic for triggering workflows                                  | string   | `workflow-trigger-topic`                |
| `cloud_function_name`         | The name of the Cloud Function to listen to Pub/Sub and trigger Cloud Run Jobs          | string   | `workflow-trigger-function`             |
| **// Workflows Jobs**         |                                                                                         |          |                                         |
| `hello_world_job_name`        | The name of the Cloud Run Job for the hello_world workflow                              | string   | `hello-world-job`                       |
| **// Secret Manager Variables** |                                                                                       |          |                                         |
| `git_token_value`             | A git access token to be stored in Secret Manager                                       | string   |                                         |

---

## Deploying New Workflows Versions

The default Docker image used in the Cloud Run Jobs is `gcr.io/google-containers/busybox`. You can replace by rebuilding the Docker images for the workflows and pushing them to Google Container Registry.

```bash
make build-and-push
```

Then, you can redeploy the latest version of the Cloud Run Jobs by running:

```bash
make deploy-jobs
```

---

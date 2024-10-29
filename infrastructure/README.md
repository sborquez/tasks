# Infrastructure Setup with Terraform

This project uses Terraform to automate the setup of Google Cloud Platform (GCP) resources, including service accounts and necessary permissions for Cloud Run and Cloud Build.

## Prerequisites

1. **Terraform**: Ensure you have Terraform installed on your machine. You can download it from [here](https://www.terraform.io/downloads.html).
2. **Google Cloud SDK**: Ensure you have the Google Cloud SDK installed and configured with the appropriate credentials. You can download it from [here](https://cloud.google.com/sdk/docs/install).
3. Your account must have the necessary permissions to create resources in the GCP project. You can use the `Owner` role or have the following permissions:


```bash
export PROJECT_ID="..."
export EMAIL="..."

export GIT_TOKEN="..."
# Other Secrets
```

```bash
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

## Setup Instructions

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
terraform plan -var="project_id=$PROJECT_ID" -var="cloud_function_name=$CLOUD_FUNCTION_NAME" -var="git_token_value=$GIT_TOKEN"
```

Replace `$PROJECT_ID` and `GIT_TOKEN`with your actual GCP project ID and GitHub or Gitlab token.

### 3. Apply the Terraform Configuration

To create the resources defined in the Terraform configuration, apply the configuration:


```
terraform apply \
  -var="project_id=$PROJECT_ID" \
  -var="cloud_function_name=$CLOUD_FUNCTION_NAME" \
  -var="git_token_value=$GIT_TOKEN" \
  -auto-approve
```

Terraform will create the necessary resources in your GCP project. The `-auto-approve` flag is used to automatically approve the plan without requiring user confirmation.

## Resources Created

### 1. APIs Enabled

- **Cloud Run API** (`run.googleapis.com`): Required for deploying and managing applications in Cloud Run.
- **Cloud Build API** (`cloudbuild.googleapis.com`): Required for using Google Cloud Build to automate the build and deployment process.
- **Container Registry API** (`containerregistry.googleapis.com`): Required for storing Docker images in Google Container Registry.
- **Cloud Functions API** (`cloudfunctions.googleapis.com`): Required for deploying and managing Cloud Functions.
- **Cloud Pub/Sub API** (`pubsub.googleapis.com`): Required for using Google Cloud Pub/Sub to publish and subscribe to messages.
- **Secret Manager API** (`secretmanager.googleapis.com`): Required for storing and managing secrets in Google Secret Manager.


### 2. Permissions and Service Accounts

- **Cloud Run invoker role**: A custom role that allows users to invoke Cloud Run services. Given to the trigger Cloud Function service account.


### 3. Pub/Sub Topic and Subscription

- **Pub/Sub Topic**: A Pub/Sub topic that triggers the Cloud Function when a message is published to the topic.
- **Pub/Sub Subscription**: A Pub/Sub subscription that listens to the Pub/Sub topic and triggers the Cloud Function.
- **Cloud Function**: A Cloud Function that is triggered by messages published to the Pub/Sub topic to run the workflows


### 4. Secrets

- **GitHub Token**: A secret that stores the GitHub token used to authenticate with the GitHub API.

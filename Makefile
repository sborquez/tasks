PROJECT_ID = $(shell gcloud config get-value project)
REGION = us-central1
FIRESTORE_DATABASE = "(default)"
REPOSITORY_NAME = "tasks-images"
TASK_API_SA = "tasks-api-sa"
TASK_JOBS_SA = "tasks-jobs-sa"
TASK_API_IMAGE_NAME = "tasks-api-server"
TASK_CORE_IMAGE_NAME = "tasks-core"

.PHONY: infra-apply build-and-push-api build-and-push-tasks

# Apply Terraform infrastructure
infra-apply:
	@echo "Applying Terraform infrastructure..."
	cd ./infrastructure && \
		terraform init -upgrade && \
		terraform apply -auto-approve \
			-var="project_id=$(PROJECT_ID)"


# Cloud Build and push Docker image
build-and-push-api:
	@echo "Building and pushing Docker image for Tasks API..."
	cd ./api && \
		gcloud builds submit --region=$(REGION) --config cloudbuild.yaml \
			--substitutions=_PROJECT_ID=$(PROJECT_ID),_REGION=$(REGION),_FIRESTORE_DATABASE=$(FIRESTORE_DATABASE),_REPOSITORY_NAME=$(REPOSITORY_NAME),_IMAGE_NAME=$(TASK_API_IMAGE_NAME),_SERVICE_ACCOUNT=$(TASK_API_SA),_SERVICE_ACCOUNT_JOBS=$(TASK_JOBS_SA)

build-and-push-task-core:
	@echo "Building and pushing Docker images for Tasks Jobs..."
	cd ./tasks/core && \
		gcloud builds submit --region=$(REGION) --config cloudbuild.yaml \
			--substitutions=_PROJECT_ID=$(PROJECT_ID),_REGION=$(REGION),_FIRESTORE_DATABASE=$(FIRESTORE_DATABASE),_REPOSITORY_NAME=$(REPOSITORY_NAME),_CORE_IMAGE=$(TASK_CORE_IMAGE_NAME)

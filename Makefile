PROJECT_ID = $(shell gcloud config get-value project)
REGION = us-central1
FIRESTORE_DATABASE = "(default)"
REPOSITORY_NAME = "tasks-images"
TASK_API_SA = "tasks-api-service-account"
TASK_JOBS_SA = "tasks-jobs-service-account"
TASK_API_IMAGE_NAME = "tasks-api-server"
TASKS = "hello_world"

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

build-and-push-tasks:
	@echo "Building and pushing Docker images for Tasks Jobs..."
	cd ./tasks && \
		gcloud builds submit --region=$(REGION) --config cloudbuild.yaml \
			--substitutions=_PROJECT_ID=$(PROJECT_ID),_REGION=$(REGION),_FIRESTORE_DATABASE=$(FIRESTORE_DATABASE),_REPOSITORY_NAME=$(REPOSITORY_NAME),_IMAGE_NAME=$(TASK_API_IMAGE_NAME),_SERVICE_ACCOUNT=$(TASK_API_SA),_SERVICE_ACCOUNT_JOBS=$(TASK_JOBS_SA),_TASKS=tasks \

# # Deploy Cloud Run jobs new revision
# deploy-jobs:
# 	@echo "Updating Cloud Run Jobs..."
# 	@echo "Updating hello-world-job..."
# 	gcloud run jobs update hello-world-job \
# 	    --image gcr.io/$(PROJECT_ID)/$(WORKFLOW_IMAGE):$(WORKFLOW_TAG) \
# 	    --region $(REGION) \
# 	    --set-env-vars WORKFLOW_NAME=hello_world \
# 	    --max-retries 3
# 	@echo "Updating push-feature-job..."
# 	gcloud run jobs update push-feature-job \
# 	    --image gcr.io/$(PROJECT_ID)/$(WORKFLOW_IMAGE):$(WORKFLOW_TAG) \
# 	    --region $(REGION) \
# 	    --set-env-vars WORKFLOW_NAME=push_feature \
# 	    --max-retries 3
# 	# @echo "Updating push-feature-job..."
# 	# gcloud run jobs update push-feature-job \
# 	#     --image gcr.io/$(PROJECT_ID)/$(WORKFLOW_IMAGE):$(WORKFLOW_TAG) \
# 	#     --region $(REGION) \
# 	#     --set-env-vars WORKFLOW_NAME=push_feature \
# 	#     --max-retries 3

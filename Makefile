.PHONY: create-env test format

PROJECT_ID = $(shell gcloud config get-value project)
PUBSUB_TOPIC = workflow-trigger
CLOUD_FUNCTION_NAME = workflow-trigger-function
REGION = us-central1

WORKFLOW_IMAGE = workflows
WORKFLOW_TAG = latest

# Create conda environment and install dependencies
create-env:
	conda create --name workflows-env python=3.10 -y
	conda activate workflows-env
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

# Run tests
test:
	python -m pytest tests/

# Run formatting with ruff
format:
	ruff check --fix .
	ruff format .

.PHONY: infra-apply build-local build-push deploy-jobs

# Apply Terraform infrastructure
infra-apply:
	@echo "Applying Terraform infrastructure..."
	cd infrastructure/workflow_trigger && zip -r "../$(CLOUD_FUNCTION_NAME)-source.zip" .
	cd ./infrastructure && terraform apply -auto-approve \
		-var="project_id=$(PROJECT_ID)" \
		-var="cloud_function_name=$(CLOUD_FUNCTION_NAME)"

# Build and push Docker image Locally
build-local:
	@echo "Building Docker image..."
	docker build -t $(WORKFLOW_IMAGE):$(WORKFLOW_TAG) .

push-local:
	@echo "Pushing Docker image..."
	docker tag $(WORKFLOW_IMAGE):$(WORKFLOW_TAG) gcr.io/$(PROJECT_ID)/$(WORKFLOW_IMAGE):$(WORKFLOW_TAG)
	docker push gcr.io/$(PROJECT_ID)/$(WORKFLOW_IMAGE):$(WORKFLOW_TAG)

run-local:
	@echo "Running Docker image..."
	docker run (WORKFLOW_IMAGE):$(WORKFLOW_TAG)

# Cloud Build and push Docker image
build-and-push:
	@echo "Building and pushing Docker image..."
	gcloud builds submit --tag gcr.io/$(PROJECT_ID)/$(WORKFLOW_IMAGE):$(WORKFLOW_TAG)

# Deploy Cloud Run jobs new revision
deploy-jobs:
	@echo "Updating Cloud Run Jobs..."
	@echo "Updating hello-world-job..."
	gcloud run jobs update hello-world-job \
	    --image gcr.io/$(PROJECT_ID)/$(WORKFLOW_IMAGE):$(WORKFLOW_TAG) \
	    --region $(REGION) \
	    --set-env-vars WORKFLOW_NAME=hello_world \
	    --max-retries 3
	# @echo "Updating push-feature-job..."
	# gcloud run jobs update push-feature-job \
	#     --image gcr.io/$(PROJECT_ID)/$(WORKFLOW_IMAGE):$(WORKFLOW_TAG) \
	#     --region $(REGION) \
	#     --set-env-vars WORKFLOW_NAME=push_feature \
	#     --max-retries 3
	# @echo "Updating push-feature-job..."
	# gcloud run jobs update push-feature-job \
	#     --image gcr.io/$(PROJECT_ID)/$(WORKFLOW_IMAGE):$(WORKFLOW_TAG) \
	#     --region $(REGION) \
	#     --set-env-vars WORKFLOW_NAME=push_feature \
	#     --max-retries 3

.PHONY: deploy-function create-pubsub-topic
PROJECT_ID = $(shell gcloud config get-value project)
PUBSUB_TOPIC = workflow-trigger
TRIGGER_CLOUD_FUNCTION_NAME = workflow-trigger-function

REGION = us-central1

WORKFLOW_IMAGE = workflows
WORKFLOW_TAG = latest

.PHONY: create-env test format
# Create conda environment and install dependencies
create-env:
	conda create --name workflows-env python=3.12 -y
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

.PHONY: infra-apply build-local push-local run-local build-and-push deploy-jobs

# Apply Terraform infrastructure
infra-apply:
	@echo "Applying Terraform infrastructure..."
	cd infrastructure/workflow_trigger && zip -r "../$(TRIGGER_CLOUD_FUNCTION_NAME)-source.zip" .
	cd infrastructure/workflow_http_pub/push_feature_request  && zip -r "../push_feature_request-source.zip" .
	cd ./infrastructure && terraform apply -auto-approve \
		-var="project_id=$(PROJECT_ID)" \
		-var="trigger_cloud_function_name=$(TRIGGER_CLOUD_FUNCTION_NAME)"

# Build and push Docker image Locally
build-local:
	@echo "Building Docker image..."
	docker build \
		--build-arg PIP_TOKEN=$(PIP_TOKEN) \
		--build-arg PLUSCODER_TOKEN=$(PLUSCODER_TOKEN) \
		-t $(WORKFLOW_IMAGE):$(WORKFLOW_TAG) .

run-local:
	@echo "Running Docker image..."
	docker run (WORKFLOW_IMAGE):$(WORKFLOW_TAG)

# Cloud Build and push Docker image
build-and-push:
	@echo "Building and pushing Docker image..."
	gcloud builds submit --config cloudbuild.yaml \
		--substitutions=_IMAGE_NAME=gcr.io/$(PROJECT_ID)/$(WORKFLOW_IMAGE):$(WORKFLOW_TAG),_PIP_TOKEN=$(PIP_TOKEN),_PLUSCODER_TOKEN=$(PLUSCODER_TOKEN)

# Deploy Cloud Run jobs new revision
deploy-jobs:
	@echo "Updating Cloud Run Jobs..."
	@echo "Updating hello-world-job..."
	gcloud run jobs update hello-world-job \
	    --image gcr.io/$(PROJECT_ID)/$(WORKFLOW_IMAGE):$(WORKFLOW_TAG) \
	    --region $(REGION) \
	    --set-env-vars WORKFLOW_NAME=hello_world \
	    --max-retries 3
	@echo "Updating push-feature-job..."
	gcloud run jobs update push-feature-job \
	    --image gcr.io/$(PROJECT_ID)/$(WORKFLOW_IMAGE):$(WORKFLOW_TAG) \
	    --region $(REGION) \
	    --set-env-vars WORKFLOW_NAME=push_feature \
	    --max-retries 3
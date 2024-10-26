.PHONY: create-env test format

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
	cd terraform && terraform apply -auto-approve

# Build and push Docker image
build-local:
	@echo "Building Docker image..."
	docker build -t workflows:latest .

build-push:
	@echo "Building and pushing Docker image..."
	docker build -t gcr.io/$(PROJECT_ID)/workflows:latest .
	docker push gcr.io/$(PROJECT_ID)/workflows:latest

# Deploy Cloud Run jobs
deploy-jobs:
	@echo "Deploying Cloud Run Jobs..."
	gcloud beta run jobs create push-feature-job \
	    --image gcr.io/$(PROJECT_ID)/workflows:latest \
	    --region us-central1 \
	    --set-env-vars WORKFLOW=push_feature \
	    --max-retries 3
	gcloud beta run jobs create gitlab-pull-request-job \
	    --image gcr.io/$(PROJECT_ID)/workflows:latest \
	    --region us-central1 \
	    --set-env-vars WORKFLOW=gitlab_pull_request \
	    --max-retries 3
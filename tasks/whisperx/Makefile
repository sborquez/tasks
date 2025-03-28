PROJECT_ID=$(shell gcloud config get-value project)
REGION=us-central1
FIRESTORE_DATABASE="(default)"
REPOSITORY_NAME=tasks-images
CORE_IMAGE=tasks-core
CORE_IMAGE_TAG=latest
TASK_JOBS_SA=tasks-jobs-sa
TASK=whisperx
TASK_MODULE=whisperx
TASK_IMAGE=tasks-whisperx
TASK_IMAGE_TAG=latest

.PHONY: venv
venv:
	python3 -m venv venv
	. venv/bin/activate
	pip install -r requirements.txt

.PHONY: install
build-python:
	pip install -e .

.PHONY: build-locally
build-locally:
	docker build --load --build-arg CORE_IMAGE=$(CORE_IMAGE):$(CORE_IMAGE_TAG)  -t $(TASK_IMAGE):$(TASK_IMAGE_TAG) .

.PHONY: build-and-push-task
build-and-push-task:
	@echo "Building and pushing Docker image for Tasks Job..."
	gcloud builds submit --region=$(REGION) --config cloudbuild.yaml \
		--substitutions=_PROJECT_ID=$(PROJECT_ID),_REGION=$(REGION),_FIRESTORE_DATABASE=$(FIRESTORE_DATABASE),_REPOSITORY_NAME=$(REPOSITORY_NAME),_CORE_IMAGE=$(CORE_IMAGE),_SERVICE_ACCOUNT=$(TASK_JOBS_SA),_TASK=$(TASK),_TASK_MODULE=$(TASK_MODULE)
CORE_IMAGE=tasks-core
CORE_IMAGE_TAG=latest

TASK_IMAGE=tasks-hello-world
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
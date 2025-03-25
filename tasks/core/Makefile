CORE_IMAGE=tasks-core
CORE_IMAGE_TAG=latest

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
	docker build --load -t $(CORE_IMAGE):$(CORE_IMAGE_TAG) .
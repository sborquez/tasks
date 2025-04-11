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


.PHONY: build-locally-cpu
build-locally-cpu:
	docker build --load -t $(CORE_IMAGE):cpu-$(CORE_IMAGE_TAG) -f Dockerfile.cpu .

.PHONY: build-locally-gpu
build-locally-gpu:
	docker build --load -t $(CORE_IMAGE):gpu-$(CORE_IMAGE_TAG) -f Dockerfile.gpu .
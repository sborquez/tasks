.PHONY: venv
venv:
	python3 -m venv venv
	. venv/bin/activate
	pip install -r requirements.txt

.PHONY: run-dev
run-dev:
	export FIRESTORE_EMULATOR_HOST=localhost:8080
	export GCLOUD_PROJECT=demo-project
	fastapi dev app/main.py --reload --port 5000

.PHONY: start-emulator
start-emulator:	## Start the firestore emulator
	cd .emulator && docker compose up -d

.PHONY: stop-emulator
stop-emulator:	## Stop the firestore emulator
	cd .emulator && docker compose down
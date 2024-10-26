
# **Workflows - Automated Git and GitLab Workflow Orchestration**

This project, named **Workflows**, implements automated workflows using **Python** and **Prefect**. The workflows are designed to handle various Git and GitLab operations such as pushing features, creating pull requests, and interacting with **PlusCoder**. These workflows run as **Cloud Run Jobs** on Google Cloud, triggered dynamically via **Google Cloud Pub/Sub** and a **Cloud Function**, with infrastructure managed using **Terraform**.

---

## **Project Structure**

```plaintext
Workflows/
├── workflows/               # Workflow definitions
│   ├── tasks/               # Individual task definitions
│   │   ├── git.py
│   │   ├── utility.py
│   │   ├── gitlab.py
│   │   └── pluscoder.py
│   ├── __main__.py          # Entry point for Prefect workflows
│   ├── hello_world.py
│   ├── push_feature.py
│   └── resolve_issue.py
├── infrastructure/          # Terraform files for infrastructure
│   ├── main.tf
│   ├── variables.tf
│   └── outputs.tf
├── tests/                   # Unit tests for workflows
├── Makefile                 # Makefile for deployment instructions
├── Dockerfile               # Dockerfile for Cloud Run Job
├── requirements.txt         # Python dependencies
├── pubsub_function/         # Cloud Function to trigger Cloud Run Jobs
│   └── main.py              # Cloud Function code
└── README.md                # Project documentation
```

---

## **Installation**

To set up the project environment and install dependencies, follow these steps:

1. Clone the repository:
   ```
   git clone https://github.com/your-username/workflows.git
   cd workflows
   ```

2. Create a conda environment and install dependencies:
   ```
   make create-env
   ```

   This command creates a conda environment named 'workflows-env' and installs all necessary dependencies.

3. Activate the conda environment:
   ```
   conda activate workflows-env
   ```

## **Development**

### Features Status

- [x] **git tasks**: Tasks for cloning repositories, creating branches, and pushing changes.
- [x] **utility tasks**: Utility tasks for notifications and logging.
- [x] **hello_world**: Simple workflow to clone a repository, create a new branch, and push changes.
- [x] **Dockers Deployment**: Build and push Docker images for workflows.
- [ ] **Cloud Infrastructure**: Set up Cloud Run Jobs, Pub/Sub, and Cloud Function for workflow orchestration with Terraform.
- [ ] **Cloud Function Trigger**: Listen to Pub/Sub messages and trigger Cloud Run Jobs with extra arguments.
- [ ] **pluscoder tasks**: Interact with PlusCoder for specific development tasks.
- [ ] **push_feature**: Automate the process of cloning a repository, creating a new feature branch, adding changes, and pushing to the branch.
- [ ] **resolve_issue**: Automate resolving a GitLab issue, including pushing a branch with changes, creating a merge request, and notifying completion.


### Running Tests

To run the test suite:

```
make test
```

### Code Formatting

To format the code using ruff:

```
make format
```

---

### Setting Up Git Token

#### Setting Up GCP for Cloud Run Job

To securely use your Git token for Git operations in Cloud Run Jobs, follow these steps:

* Store the Token in GCP Secret Manager
    1. Navigate to Secret Manager in the GCP Console.
    2. Create a New Secret with the name `GIT_TOKEN`.

* Configure Cloud Run to Access the Secret
    1. When deploying your Cloud Run Job, mount the secret as an environment variable `GIT_TOKEN`.
    2. Ensure the Cloud Run service account has the “Secret Manager Secret Accessor” role.

#### Running Locally with Docker

To run the application locally using Docker with the --env option, follow these steps:

* `docker run -e GIT_TOKEN workflows:latest ...`

## **Workflows Overview**

The project includes two key workflows, defined using **Prefect**:

1. **hello_world**: A simple workflow that clone a repository, creates a new branch called `hello-world`, and pushes changes to the branch.
2. **push_feature**: Automates the process of cloning a repository, creating a new feature branch, adding (PlusCoder) and pushing changes, and notifying completion.
3. **resolve_issue**: Automates resolving a GitLab issue. including, pushing a branch with the changes, creating a merge request, and notifying completion.

### **Task Overview**

- **git.py**: Contains tasks for cloning repositories, creating branches, and pushing changes.
- **utility.py**: Contains utility tasks such as notifications and logging.
- **gitlab.py**: Handles interactions with GitLab, such as creating pull requests.
- **pluscoder.py**: Interacts with PlusCoder for specific development tasks.

---

## **Cloud Infrastructure**

This project runs workflows as **Cloud Run Jobs**, triggered by **Pub/Sub** messages, which are sent to a **Cloud Function**. The infrastructure is managed using **Terraform**.

### **Key Components**:

- **Cloud Run Jobs**: Executes Prefect workflows packaged in Docker. Each Cloud Run Job is created with a specific workflow defined at the creation phase.
- **Google Cloud Pub/Sub**: Used to publish messages that trigger workflows with extra arguments.
- **Cloud Function**: Listens to Pub/Sub and triggers the specific Cloud Run Job, passing extra arguments (e.g., repository details, feature name).
- **Terraform**: Manages infrastructure as code, deploying Pub/Sub topics, Cloud Functions, and Cloud Run Jobs.

---

## **Cloud Function Trigger**

The **Google Cloud Function** listens for messages published to a **Google Cloud Pub/Sub** topic. Upon receiving a message, the Cloud Function triggers the pre-defined **Cloud Run Job** for the workflow (set during job creation), passing any extra arguments specified in the Pub/Sub message.

### **Cloud Function Logic**:

1. The workflow is **already defined** during the job creation phase and is not passed in the Pub/Sub message.
2. The Pub/Sub message contains **only extra arguments** (e.g., feature name, branch name) for the workflow.
3. The Cloud Function uses the **Google Cloud Run API** to trigger the pre-configured Cloud Run Job, passing the extra arguments.

#### **Cloud Function Code (pubsub_function/main.py)**

```python
import base64
import json
import os
from googleapiclient.discovery import build
from google.oauth2 import service_account

def trigger_workflow(event, context):
    """Triggered from a message on a Cloud Pub/Sub topic."""
    pubsub_message = base64.b64decode(event['data']).decode('utf-8')
    message_data = json.loads(pubsub_message)

    job_name = message_data.get('job_name')
    args = message_data.get('args', [])

    if not job_name:
        print("No job_name provided in the Pub/Sub message.")
        return

    # Authenticate and trigger Cloud Run Job
    credentials = service_account.IDTokenCredentials.from_service_account_file(
        'service-account.json',
        target_audience='https://run.googleapis.com/'
    )
    client = build('run', 'v1', credentials=credentials)

    parent = f"projects/{os.getenv('GCP_PROJECT')}/locations/{os.getenv('GCP_REGION')}/jobs/{job_name}"
    request = client.projects().locations().jobs().run(name=parent, body={"args": args})
    response = request.execute()

    print(f"Job {job_name} triggered with response: {response}")
```

### **Cloud Function Deployment**

1. **Deploy Cloud Function**:
   The Cloud Function is deployed using **Terraform**. It listens to the Pub/Sub topic, and when a message is received, it triggers the appropriate Cloud Run Job based on the job name defined during the job creation phase.

2. **Pub/Sub Topic**:
   The topic used by the Cloud Function is managed via Terraform. This topic is where you publish messages containing extra arguments for the workflow.

---

## **Deployment Steps**

The project includes a **Makefile** to simplify deployment.

### **1. Infrastructure Setup (Terraform)**

Run the following commands to set up the infrastructure using Terraform:

```bash
make infra-apply
```

This command runs the necessary `terraform apply` commands, setting up Pub/Sub, Cloud Functions, and Cloud Run Jobs.

### **2. Build and Push Docker Image**

To build and push the Docker image for the workflows, use the following command:

```bash
make build-push
```

This will build the Docker image and push it to Google Container Registry.

### **3. Deploy Cloud Run Jobs**

After building the Docker image, deploy the **Cloud Run Jobs** for the workflows using:

```bash
make deploy-jobs
```

This command will deploy Cloud Run Jobs for `push_feature` and `gitlab_pull_request`. The workflow for each job is defined during the job creation phase.

---

## **Makefile**

The **Makefile** provides a simple way to deploy and manage the infrastructure and workflows.

```Makefile
.PHONY: infra-apply build-push deploy-jobs

infra-apply:
	@echo "Applying Terraform infrastructure..."
	cd terraform && terraform apply -auto-approve

build-push:
	@echo "Building and pushing Docker image..."
	docker build -t gcr.io/your-project-id/workflows:latest .
	docker push gcr.io/your-project-id/workflows:latest

deploy-jobs:
	@echo "Deploying Cloud Run Jobs..."
	gcloud beta run jobs create push-feature-job \
	    --image gcr.io/your-project-id/workflows:latest \
	    --region us-central1 \
	    --set-env-vars WORKFLOW=push_feature \
	    --max-retries 3
	gcloud beta run jobs create gitlab-pull-request-job \
	    --image gcr.io/your-project-id/workflows:latest \
	    --region us-central1 \
	    --set-env-vars WORKFLOW=gitlab_pull_request \
	    --max-retries 3
```

---

## **Usage**

1. **Run Workflows**: Use the `make deploy-jobs` command to deploy workflows. Publish a message to the Pub/Sub topic with **extra arguments only**:

   ```bash
   gcloud pubsub topics publish trigger-workflow-topic        --message '{"job_name": "push-feature-job", "args": ["--repo=git@github.com:user/repo.git", "--branch=feature-branch"]}'
   ```

2. **Monitor Jobs**: Use Google Cloud Console to monitor job execution in Cloud Run.

---

## **Configuration**

- **Workflows**: Each workflow is defined at the time of Cloud Run Job creation and cannot be changed dynamically at runtime.
- **Extra Arguments**: The Pub/Sub message only passes extra arguments specific to the job, such as the repository URL or feature branch.
- **Environment Variables**: Sensitive information such as GitLab tokens should be handled using environment variables or Secret Manager.

---

## **Contributing**

1. Fork the repository.
2. Create a new feature branch.
3. Submit a pull request.

---

## **License**

This project is licensed under the MIT License.

---

This updated README reflects the change that the workflow is defined during Cloud Run Job creation, and only extra arguments for the workflow are passed via Pub/Sub. Let me know if further modifications are needed!

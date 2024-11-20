
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
│   ├── outputs.tf
│   ├── workflow_trigger/      # Cloud Function code
│   │   ├── requirements.txt
│   │   └── main.py
│   └── workflow_http_pub/     # HTTP-triggered Cloud Functions
│       └── push_feature_request/
│           ├── main.py
│           └── requirements.txt
├── tests/                   # Unit tests for workflows
├── Makefile                 # Makefile for deployment instructions
├── Dockerfile               # Dockerfile for Cloud Run Job
├── requirements.txt         # Python dependencies
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
- [x] **Cloud Infrastructure**: Set up Cloud Run Jobs, Pub/Sub, and Cloud Function for workflow orchestration with Terraform.
- [x] **Cloud Function Trigger**: Listen to Pub/Sub messages and trigger Cloud Run Jobs with extra arguments.
- [x] **pluscoder tasks**: Interact with PlusCoder for specific development tasks.
- [x] **push_feature**: Automate the process of cloning a repository, creating a new feature branch, adding changes, and pushing to the branch.
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

### Setting Up Secret Tokens

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
- **Cloud Functions**:
  - **Workflow Trigger**: Listens to Pub/Sub and triggers the specific Cloud Run Job, passing extra arguments (e.g., repository details, feature name).
  - **Push Feature Request**: Handles HTTP requests to initiate the push feature workflow.
- **Terraform**: Manages infrastructure as code, deploying Secrets, Pub/Sub topics, Cloud Functions, and Cloud Run Jobs.

### **Infrastructure Details**:

1. **Pub/Sub Topic**: A topic is created to receive messages for triggering workflows.
2. **Cloud Function**:
   - Listens to the Pub/Sub topic
   - Decodes incoming messages
   - Determines which Cloud Run Job to trigger based on the message content
   - Triggers the appropriate Cloud Run Job using the Cloud Run API
3. **Cloud Run Jobs**:
   - A job is created for the hello_world workflow
   - Jobs for other workflows (e.g., push_feature, gitlab_pull_request) can be added as needed
4. **IAM Permissions**: The Cloud Function is granted necessary permissions to trigger Cloud Run Jobs
5. **APIs**: Required APIs (cloudfunctions.googleapis.com, pubsub.googleapis.com) are enabled
6. **Secrets**: Sensitive information such as GitLab tokens can be stored in Secret Manager and accessed by Cloud Run Jobs.

All these components are defined and managed using Terraform, ensuring consistent and reproducible infrastructure deployment.

---

## **Cloud Function Trigger**

The **Google Cloud Function** listens for messages published to a **Google Cloud Pub/Sub** topic. Upon receiving a message, the Cloud Function decodes it, determines which **Cloud Run Job** to trigger, and starts the job with the provided parameters.

### **Cloud Function Logic**:

1. **Decode Pub/Sub message**: The function decodes the base64-encoded message from the Pub/Sub event.
2. **Determine workflow**: It uses the 'workflow' field in the message to determine which Cloud Run Job to trigger.
3. **Parse parameters**: The function extracts and formats the parameters from the 'parameters' field in the message.
4. **Retrieve project and region**: It programmatically gets the Google Cloud Project ID and region.
5. **Trigger Cloud Run Job**: Using the Cloud Run API, it starts the specified job with the parsed parameters.

### **Pub/Sub Message Structure**:

The Pub/Sub message structure is as follows:

```json
{
  "workflow": "workflow_name",
  "parameters": {
    "param1": "value1",
    "param2": "value2",
    ...
  }
}
```

#### Sending a Pub/Sub Message:

```bash
gcloud pubsub topics publish workflow-trigger-topic --message '{"workflow": "workflow_name", "parameters": {"param1": "value1", "param2": "value2", ...}}'
```

Examples:

- **hello_world Workflow**:
```bash
gcloud pubsub topics publish workflow-trigger-topic --message '{"workflow": "hello_world", "parameters": {"git_url": "https://github.com/sborquez/studious-giggle.git", "git_user": "Sebastián Bórquez", "git_email": "sebastian.borquez.g@gmail.com"}}'
```

- **push_feature Workflow**:
```bash
gcloud pubsub topics publish workflow-trigger-topic --message '{"workflow": "push_feature", "parameters": {"author": "Sebastian Borquez", "feature_request": "Add a main.py file that prints -Hello, World!-", "git_url": "https://github.com/sborquez/studious-giggle.git", "source_branch": "main"}}'
```

### **Cloud Function Deployment**

1. **Deploy Cloud Function**:
   The Cloud Function is deployed using **Terraform**. It listens to the Pub/Sub topic and triggers the appropriate Cloud Run Job based on the workflow specified in the message.

2. **Pub/Sub Topic**:
   The topic used by the Cloud Function is managed via Terraform. This topic is where you publish messages to trigger workflows with specific parameters.

3. **Environment Variables**:
   The Cloud Function uses environment variables to map workflow names to their corresponding Cloud Run Job names. These are set during deployment and follow the format `WORKFLOW_NAME_JOB_NAME`.

---

## **Deployment Steps**

The project includes a **Makefile** to simplify deployment.

### **1. Infrastructure Setup (Terraform)**

Run the following command to set up the infrastructure using Terraform:

```bash
make infra-apply
```

This command runs the necessary `terraform apply` commands, setting up:
- Pub/Sub topic
- Cloud Function
- Cloud Run Job for hello_world workflow
- IAM permissions
- Required APIs

### **2. Build and Push Docker Image**

#### Prerequisites
Ensure you have the required tokens:
- PIP_TOKEN: For package installation
- PLUSCODER_TOKEN: For PlusCoder integration

#### Using Cloud Build
The project uses Cloud Build with configuration from `cloudbuild.yaml`. To build:

1. Set required tokens:
```bash
export PIP_TOKEN=your_pip_token
export PLUSCODER_TOKEN=your_pluscoder_token
```

2. Build and push:
```bash
make build-and-push
```

This builds using Cloud Build configuration and pushes to Google Container Registry.

### **3. Deploy Cloud Run Jobs**

After building the Docker image, deploy the **Cloud Run Jobs** for the workflows using:

```bash
make deploy-jobs
```

This command will update the deployed Cloud Run Jobs for the defined workflows. The workflow for each job is defined during the infrastructure setup phase.

### **4. Deploy HTTP-triggered Cloud Functions**

To deploy the Push Feature Request Function, use the following command:

```bash
make deploy-http-functions
```

This command will deploy the HTTP-triggered Cloud Functions, including the Push Feature Request Function.

### **5. Verify Deployment**

After deployment, verify that:
- The Pub/Sub topic is created
- The Cloud Functions (Workflow Trigger and Push Feature Request) are deployed and configured correctly
- The Cloud Run Jobs are created and ready to be triggered
- IAM permissions are correctly set

You can use the Google Cloud Console or `gcloud` CLI commands to verify these components.

---

## **Push Feature Request Function**

The Push Feature Request Function is an HTTP-triggered Cloud Function that handles requests to initiate the push feature workflow. It's located in `infrastructure/workflow_http_pub/push_feature_request/main.py`.

### Purpose
This function receives HTTP POST requests, processes the payload, and publishes a message to a Pub/Sub topic to trigger the push feature workflow.

### Parameters
The function accepts the following parameters in the JSON payload:

- `git_url` (required): The URL of the Git repository.
- `feature_request` (required): The description of the feature to be implemented.
- `source_branch` (optional): The source branch to create the feature from.
- `feature_branch` (optional): The name of the new feature branch.
- `author` (optional): The author of the feature request.
- `git_user` (optional): The Git username for commits.
- `git_email` (optional): The Git email for commits.
- `agent` (optional): The agent to use for the workflow.
- `model` (optional): The model to use for the workflow.
- `provider` (optional): The provider to use for the workflow.
- `extra_flags` (optional): Any additional flags for the workflow.

### Usage Example
To trigger the push feature workflow using this function, send a POST request with a JSON payload. Here's an example using `curl`:

```bash
curl -X POST https://YOUR_REGION-YOUR_PROJECT_ID.cloudfunctions.net/push_feature_request \
     -H "Content-Type: application/json" \
     -d '{
           "git_url": "https://github.com/example/repo.git",
           "feature_request": "Add a new login page",
           "source_branch": "main",
           "author": "John Doe",
           "git_user": "johndoe",
           "git_email": "john@example.com"
         }'
```

Replace `YOUR_REGION` and `YOUR_PROJECT_ID` with your actual Google Cloud region and project ID.

The function will process this request, create a message with the provided parameters, and publish it to the specified Pub/Sub topic, which will then trigger the push feature workflow.

---

## **License**

This project is licensed under the MIT License.

---

This updated README reflects the change that the workflow is defined during Cloud Run Job creation, and only extra arguments for the workflow are passed via Pub/Sub. Let me know if further modifications are needed!

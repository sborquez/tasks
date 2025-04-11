
# **Tasks - Automated Tasks with Python**

The tasks are designed to handle various sequential steps to achieve a task, such as pushing features, creating pull requests, generating images, etc. These workflows run as **Cloud Run Jobs** on Google Cloud or asynchronously triggered **Vertex AI Endpoints** (for GPU tasks).

An API server is included to handle the available workflows, their parameters, and results schemas so you can integrate them into your own applications. The API server triggers the workflows and manages their execution and results.

      Note: The Vertex AI Endpoints are not yet implemented, but the code is ready for creating an HTTP endpoint.
      We only lack the deployment of the model to the endpoint and registration of the endpoint in Firestore.


---

## **Project Structure**

```plaintext
tasks/
├── infrastructure/           # Terraform files for infrastructure
│   ├── main.tf
│   ├── variables.tf
│   └── outputs.tf
├── api/                      # API server files
│   ├── .emulator/            # Firestore emulator files
│   ├── app/                  # API server files
│   │   └── ...
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── cloudbuild.yaml
│   └── Makefile              # Makefile for API server for development
├── tasks/                    # Terraform files for infrastructure
│   ├── core/                 # Core Module for tasks
│   │   ├── tasks/
│   │   │   ├── tasks.py      # Core components for tasks
│   │   │   ├── scripts.py    # Entry points for tasks
│   │   │   └── ...
│   │   ├── Dockerfile.cpu    # Dockerfile for base images for CPU tasks
│   │   ├── Dockerfile.gpu    # Dockerfile for base images for GPU tasks
│   │   ├── cloudbuild.yaml
│   │   ├── requirements.txt
│   │   ├── pyproject.toml
│   │   └── Makefile          # Makefile for API server for development
│   ├── hello-world/          # Example CPU task
│   │   ├── hello_world/
│   │   ├── cloudbuild.yaml
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── pyproject.toml
│   │   └── Makefile          # Makefile for task deployment instructions
│   └── ...                   # Other tasks (e.g., whisperx, etc.)
├── Makefile                  # Makefile for deployment instructions
└── README.md
```

---

## **Quick Start**

This project is designed to be run on **Google Cloud Platform** (GCP) and requires a GCP account. The project uses **Terraform** for infrastructure management, **Docker** for containerization, and **Firestore** for workflow registration and execution tracking.

Before running the `Makefile` commands, ensure you have the following prerequisites:
- **Google Cloud SDK**: Install the [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) and authenticate with your GCP account.
- **Define your GCP project**: Set your GCP project ID in the `Makefile` or use the `gcloud` command to set it.
- **Terraform**: Install [Terraform](https://www.terraform.io/downloads.html) and authenticate with your GCP account.
- **Docker**: Install [Docker](https://docs.docker.com/get-docker/) and authenticate with Google Container Registry.
- **Check the Makefile**: Ensure the `Makefile` is configured with your GCP project ID and region.

1. Create the infrastructure using Terraform:

   ```bash
   make infra-apply
   ```

   This command will set up the necessary resources in GCP:
   * Enable necessary APIs
   * Service Account and IAM permissions for API server and tasks
   * Firestore database
   * Bucket for storing workflow results and model weights

2. Deploy the API server:

   ```bash
   make build-and-push-api
   ```
   This command will build the **API Server** Docker image and push it to Google Container Registry. It will also deploy the API server to **Cloud Run Service**.

3. Build base images for tasks:

   ```bash
   make build-and-push-task-core
   ```

   This command will build the Docker images for the tasks (`tasks-core`) and push them to Google Container Registry. These images (`cpu` and `gpu`) will be used to build the specific tasks images.

4. Build and push the Docker image for a task, repeating this step for each task that you want to deploy:

   ```bash
   cd tasks/<task_directory>
   make build-and-push-task
   ```

   This will build the Docker image for the task and push it to the Google Container Registry. The task will be registered in Firestore and ready to be used in workflows. Depending on the task, this will deploy it to **Cloud Run Jobs** or **Vertex AI Endpoints**.

## **Add a New Task**

To add a new task, create a directory under `tasks/` and implement the task logic in Python. You can copy the `hello-world` task as a template for `cpu` tasks, or copy the `whisperx` (`(wip) hello-world-gpu`) task as a template for `gpu` tasks.

Suppose you want to create a new task called `my-task`:
1. Copy the `hello-world` task directory to `my-task`:

   ```bash
   cp -r tasks/hello-world tasks/my-task
   mv tasks/my-task/hello_world tasks/my-task/my_task
   ```

2. Modify the `Makefile` in `tasks/my-task` to reflect the new task name and any other necessary changes.

   ```bash
   TASK=hello-world -> my-task
   TASK_MODULE=hello_world -> my_task
   TASK_IMAGE=tasks-hello-world -> tasks-my-task
   ```

3. Implement the task I/O in `tasks/my-task/my_task/` directory.
   1. You must define the `Parameters` and `Results` schemas in the `main.py` file to specify the input and output of the task:
   ```python
   class Parameters(BaseParameters):
    name: str | None = Field(
        description="The name of the hello world branch",
        default=None,
    )

   class Results(BaseResult):
      message: str = Field(
         description="The message to be printed",
      )
   ```
   2. Define the steps and task by decorating the functions with `@step` and `@task` decorators.
   ```python
   @step(name="Get Name", description="Generate a name")
   def get_name(name: str ) -> str:
      name = name or generate_name(style="capital")
      logger.info(f"Getting name: {name}")
      return name


   @step(name="Say Hello", description="Print a hello message")
   def say_hello(name: str) -> str:
      logger.info(f"Hello, {name}!")
      return f"Hello, {name}!"


   @task(name="Hello World", description="A hello world task")  # type: ignore
   def hello_world(parameters: Parameters) -> Results:
      name = get_name(parameters.name or "")
      message = say_hello(name)
      return Results(message=message)
   ```

4. And finally, build and push the task image:

   ```bash
   cd tasks/my-task
   make build-and-push-task
   ```
   You should be able to see the task registered in Firestore and ready to be used in workflows. Use the API server to trigger the task and check the results.

---

## **How does it work?**

1. Task abstraction
   1. Parameters and Results schemas
   2. task and step decorators
   3. Task registration
   4. Task execution
2. Task flow with the API server
   1. Discovery
   2. Execution
   3. Results
---

## **License**

This project is licensed under the MIT License.

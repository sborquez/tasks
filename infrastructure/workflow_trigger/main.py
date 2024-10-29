import base64
import json
import os

import requests
from google.auth import default
from google.cloud import run_v2

import functions_framework


# Initialize the Cloud Run client
client = run_v2.JobsClient()


def get_project_id():
    """Retrieve the Google Cloud Project ID programmatically."""
    # Use Google Cloud Auth library to retrieve project ID
    _, project_id = default()
    return project_id


def get_region():
    """Retrieve the Google Cloud region programmatically."""
    try:
        # Metadata server URL to get the region
        url = "http://metadata.google.internal/computeMetadata/v1/instance/region"
        headers = {"Metadata-Flavor": "Google"}
        response = requests.get(url, headers=headers)
        # The region will be returned in the form of projects/{project_number}/regions/{region}, so split to get the region.
        return response.text.split('/')[-1]
    except Exception as e:
        print(f"Error retrieving region: {e}")
        return None


def decode_pubsub_message(event):
    """Decode Pub/Sub message."""
    try:
        message = base64.b64decode(event['data']).decode('utf-8')
        return json.loads(message)
    except Exception as e:
        print(f"Error decoding message: {e}")
        return None

def determine_workflow_to_trigger(message):
    """Determine which Cloud Run Job to trigger based on the message."""
    workflow = message.get('workflow')
    return os.environ.get(f"{workflow.upper().replace('-', '_')}_JOB_NAME")

def parse_workflow_parameters(message) -> list[str]:
    """Parse and validate input parameters for a workflow."""
    parameters = message.get('parameters')
    if not parameters:
        return []
    flattened_parameters = []
    if isinstance(parameters, dict):
        for key, value in parameters.items():
            key = key if key.startswith('--') else f"--{key}"
            flattened_parameters.extend([key, str(value)])
    else:
        raise ValueError("Parameters must be a dictionary")
    return flattened_parameters

@functions_framework.cloud_event
def workflow_trigger(cloud_event):
    """Cloud Function to handle Pub/Sub trigger and start Cloud Run Job."""
    try:
        # Decode the Pub/Sub message
        pubsub_message = decode_pubsub_message(cloud_event.data["message"])
        if not pubsub_message:
            print("Failed to decode Pub/Sub message")
            return

        # Determine which job to trigger
        workflow_name = determine_workflow_to_trigger(pubsub_message)
        workflow_parameters = parse_workflow_parameters(pubsub_message)
        if not workflow_name:
            print(f"Workflow not found: {pubsub_message.get('workflow')}")
            return

        # Retrieve Project ID and Region programmatically
        project_id = get_project_id()
        region = get_region()
        if not region:
            print("Failed to retrieve region")
            return

        # Build the fully qualified job name (project/region/job)
        full_job_name = f"projects/{project_id}/locations/{region}/jobs/{workflow_name}"

        # Trigger the Cloud Run Job
        print(f"Starting job: {full_job_name}")
        print(f"Parameters: ({type(workflow_parameters)}) {workflow_parameters}")

        # Start the Cloud Run Job
        run_request = run_v2.RunJobRequest(
            name=full_job_name,  # Fully qualified job name
            overrides=run_v2.RunJobRequest.Overrides(
                container_overrides=[
                    run_v2.RunJobRequest.Overrides.ContainerOverride(
                        args=workflow_parameters
                    )
                ]
            )
        )
        operation = client.run_job(request=run_request)

        # Don't wait for the job to complete
        print(f"Job started: {operation}")

    except Exception as e:
        print(f"Error processing Pub/Sub message: {e}")

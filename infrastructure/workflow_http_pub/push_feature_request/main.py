import json
import os
from google.cloud import pubsub_v1
from google.auth import default

import functions_framework  # type: ignore


def get_project_id():
    """Retrieve the Google Cloud Project ID programmatically."""
    # Use Google Cloud Auth library to retrieve project ID
    _, project_id = default()
    return project_id


@functions_framework.http
def publish(request):
    """Cloud Function to handle HTTP request and push message to Pub/Sub topic."""

    if request.method != "POST":
        return "Only POST requests are accepted", 405

    # Get the Pub/Sub topic name from environment variable
    trigger_topic_id = os.environ.get("PUBSUB_TOPIC", "workflow-trigger-topic")
    push_feature_workflow = os.environ.get("TARGET_WORKFLOW", "push_feature")


    # Create a Publisher client
    publisher = pubsub_v1.PublisherClient()
    project_id = os.environ.get("GCP_PROJECT", get_project_id())
    topic_path = publisher.topic_path(project_id, trigger_topic_id)  # type: ignore

    # Publish the message to the topic
    json_content = request.get_json()
    parameters = {
        "git_url": json_content.get("git_url"),
        "source_branch": json_content.get("source_branch"),
        "feature_branch": json_content.get("feature_branch"),
        "author": json_content.get("author"),
        "git_user": json_content.get("git_user"),
        "git_email": json_content.get("git_email"),
        "feature_request": json_content.get("feature_request"),
        "agent": json_content.get("agent"),
        "model": json_content.get("model"),
        "provider": json_content.get("provider"),
        "extra_flags": json_content.get("extra_flags"),
    }

    # Remove None values from the parameters
    parameters = {k: v for k, v in parameters.items() if v is not None}
    print(f"Parameters: {parameters}")

    # Check non-optionals git_url and feature_request
    if not (parameters.get("git_url") and parameters.get("feature_request")):
        return "Missing required parameters", 400

    payload = {
        "workflow": push_feature_workflow,
        "parameters": parameters,
    }
    print(f"Payload: {payload}")
    message = json.dumps(payload).encode("utf-8")
    future = publisher.publish(topic_path, message)
    message_id = future.result()
    print(f"Published message to {trigger_topic_id} - {message_id}")
    return f"Published message to {trigger_topic_id} - {message_id}", 200

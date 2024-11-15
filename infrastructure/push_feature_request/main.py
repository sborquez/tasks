import json
import os
from google.cloud import pubsub_v1

import functions_framework


@functions_framework.http("POST")
def push_feature_request(request):
    """Cloud Function to handle HTTP request and push message to Pub/Sub topic."""

    # Get the Pub/Sub topic name from environment variable
    topic_name = os.environ.get("PUBSUB_TOPIC", "workflow-trigger-topic")
    push_feature_workflow = os.environ.get("PUSH_FEATURE_WORKFLOW", "push_feature")

    # Create a Publisher client
    publisher = pubsub_v1.PublisherClient()

    # Publish the message to the topic
    parameters = {
        "git_url": request.form.get("git_url"),
        "git_user": request.form.get("git_user"),
        "git_email": request.form.get("git_email"),
        "feature_request": request.form.get("feature_request"),
        "agent": request.form.get("agent"),
        "model": request.form.get("model"),
        "provider": request.form.get("provider"),
        # "extra_flags": request.form.get("extra_flags"),
    }

    # Remove None values from the parameters
    parameters = {k: v for k, v in parameters.items() if v is not None}

    # Check non-optionals git_url and feature_request
    if not parameters.get("git_url") or not parameters.get("feature_request"):
        return "Missing required parameters", 400

    payload = {
        "workflow": push_feature_workflow,
        "parameters": parameters,
    }
    message = json.dumps(payload)
    future = publisher.publish(topic_name, message)
    return f"Published message to {topic_name}", 200

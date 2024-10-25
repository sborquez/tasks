from workflows import hello_world
from pydantic import BaseModel
from typing import Type


def parse_parameters(workflow_name: str, workflow_parameters: Type[BaseModel]) -> BaseModel:
    """
    Parse and validate input parameters for a workflow.

    Args:
        workflow_name (str): Name of the workflow.
        workflow_parameters (type): Parameters model for the workflow.
    Returns:
        Parameters: Validated input parameters.

    Raises:
        ValueError: If required parameters are missing or invalid.
    """
    import argparse
    parser = argparse.ArgumentParser(
        description=f"Run {workflow_name.replace('_', ' ').title()} workflow",
    )
    # Build parser dynamically based on the Parameters model
    for name, field in workflow_parameters.__fields__.items():
        parser.add_argument(f'--{name}', required=True, help=field.description)

    args = parser.parse_args()
    parameters = workflow_parameters(**vars(args))
    return parameters


def run_workflow(workflow_name: str) -> None:
    if workflow_name == "hello_world":
        parameters = hello_world.Parameters
        flow = hello_world.workflow
    else:
        raise ValueError(f"Unknown workflow: {workflow_name}")
    # Parse and validate input parameters
    parameters = parse_parameters(workflow_name, parameters)
    flow(parameters)

if __name__ == '__main__':
    import os
    workflow_name = os.environ.get("WORKFLOW_NAME")
    if not workflow_name:
        raise ValueError("WORKFLOW_NAME environment variable is not set")
    run_workflow(workflow_name)
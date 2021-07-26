"""JSON Schema Generator Definition."""
import copy

from django_workflow_system.utils import RESPONSE_SCHEMA


def get_response_schema(workflow_step_user_input):
    """
    Create JSON Schema for responses to Free Form Question user inputs.

    Args:
        workflow_step_user_input (WorkflowStepUserInput): The WorkflowStepUserInput Object.

    Returns:
        dict: The response schema to be validated against.
    """
    response_schema = copy.deepcopy(RESPONSE_SCHEMA)

    # User input must be a string under normal circumstances.
    response_schema["properties"]["userInput"]["anyOf"] = [
        {"type": "string"},
    ]

    # But if no response is required can also be null.
    if not workflow_step_user_input.specification["meta"]["inputRequired"]:
        response_schema["properties"]["userInput"]["anyOf"].append({"type": None})

    return response_schema

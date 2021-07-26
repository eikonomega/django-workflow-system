"""JSON Schema Generator Definition."""
import copy

from django_workflow_system.utils import RESPONSE_SCHEMA


def get_response_schema(workflow_step_user_input):
    """
    Create JSON Schema for responses to True/False Question user inputs.

    Args:
        workflow_step_user_input (WorkflowStepUserInput): The WorkflowStepUserInput Object.

    Returns:
        dict: The response schema to be validated against.
    """
    response_schema = copy.deepcopy(RESPONSE_SCHEMA)

    # Scenario 1: User input is required AND must be correct... the input MUST have the correct answer.
    if all(
        [
            workflow_step_user_input.specification["meta"]["inputRequired"],
            workflow_step_user_input.specification["meta"]["correctInputRequired"],
        ]
    ):
        # Response must be a boolean.
        response_schema["properties"]["userInput"]["type"] = "boolean"
        response_schema["properties"]["userInput"][
            "const"
        ] = workflow_step_user_input.specification["correctInput"]

    # Scenario 2: User input is required, but it doesn't have to be the correct answer, just a boolean.
    if (
        workflow_step_user_input.specification["meta"]["inputRequired"]
        and not workflow_step_user_input.specification["meta"]["correctInputRequired"]
    ):
        # Response must be a boolean.
        response_schema["properties"]["userInput"]["type"] = "boolean"
        response_schema["properties"]["userInput"][
            "enum"
        ] = workflow_step_user_input.specification["inputOptions"]

    # Scenario 3: Input is not required, and therefore cannot require the correct input either.
    if not any(
        [
            workflow_step_user_input.specification["meta"]["inputRequired"],
            workflow_step_user_input.specification["meta"]["correctInputRequired"],
        ]
    ):
        # Response must be a boolean or null.
        response_schema["properties"]["userInput"]["anyOf"] = [
            {"type": "string"},
            {"type": "null"},
        ]
        response_schema["properties"]["userInput"]["enum"] = [True, False, None]

    return response_schema

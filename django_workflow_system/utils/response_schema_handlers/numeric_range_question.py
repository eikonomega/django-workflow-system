"""Response Schema Generator Module for a Numeric Range Question"""
import copy

from django_workflow_system.utils import RESPONSE_SCHEMA


def get_response_schema(workflow_step_user_input):
    """
    Build and returns a response schema for a given WorkflowStepUserInput w/
    a WorkflowStepUserInputType of 'Numeric Range Question'.

    Args:
        workflow_step_user_input (WorkflowStepUserInput): The WorkflowStepUserInput Object.

    Returns:
        dict: The response schema to be validated against.
    """
    response_schema = copy.deepcopy(RESPONSE_SCHEMA)

    # Now we need to check some things.....
    if (
        workflow_step_user_input.specification["meta"]["inputRequired"]
        and workflow_step_user_input.specification["meta"]["correctInputRequired"]
    ):
        # They need to respond with the correct answer.
        response_schema["properties"]["userInput"][
            "type"
        ] = workflow_step_user_input.type.json_schema["properties"]["correctInput"][
            "type"
        ]
        response_schema["properties"]["userInput"]["enum"] = [
            workflow_step_user_input.specification["correctInput"]
        ]

    elif (
        workflow_step_user_input.specification["meta"]["inputRequired"]
        and not workflow_step_user_input.specification["meta"]["correctInputRequired"]
    ):
        # They don't need to respond with the correct answer.
        response_schema["properties"]["userInput"][
            "type"
        ] = workflow_step_user_input.type.json_schema["properties"]["correctInput"][
            "type"
        ]
        response_schema["properties"]["userInput"]["enum"] = fetch_numbers(
            workflow_step_user_input
        )

    else:
        # Answer is not required and correct is not required, so null should be an option in potential responses
        response_schema["properties"]["userInput"]["anyOf"] = [
            {
                "type": workflow_step_user_input.type.json_schema["properties"][
                    "correctInput"
                ]["type"]
            },
            {"type": "null"},
        ]
        new_enum = fetch_numbers(workflow_step_user_input)
        new_enum.append(None)
        response_schema["properties"]["userInput"]["enum"] = new_enum

    return response_schema


def fetch_numbers(workflow_step_user_input):
    """
    Loop through and create a list of all possible numbers.

    Args:
        workflow_step_user_input (WorkflowStepUserInput): The WorkflowStepUserInput Object.

    Returns:
        list: A listt of all possible answer numbers in the given range.
    """
    number_list = []
    for number in range(
        workflow_step_user_input.specification["inputOptions"]["minimumValue"],
        workflow_step_user_input.specification["inputOptions"]["maximumValue"]
        + workflow_step_user_input.specification["inputOptions"]["step"],
        workflow_step_user_input.specification["inputOptions"]["step"],
    ):
        number_list.append(number)
    return number_list

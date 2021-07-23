"""Response Schema Generator Module for a Single Choice Question"""
import copy

from django_workflow_system.utils import RESPONSE_SCHEMA


def get_response_schema(workflow_step_user_input):
    """
    Build and returns a response schema for a given WorkflowStepUserInput w/
    a WorkflowStepUserInputType of 'Single Choice Question'.

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
            "anyOf"
        ] = workflow_step_user_input.type.json_schema["properties"]["correctInput"][
            "anyOf"
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
            "anyOf"
        ] = workflow_step_user_input.type.json_schema["properties"]["correctInput"][
            "anyOf"
        ]
        response_schema["properties"]["userInput"][
            "enum"
        ] = workflow_step_user_input.specification["inputOptions"]

    else:
        # Answer is not required and correct is not required, so null should be an option in potential responses
        new_any_of = copy.deepcopy(
            workflow_step_user_input.type.json_schema["properties"]["correctInput"][
                "anyOf"
            ]
        )
        new_any_of.append({"type": "null"})
        response_schema["properties"]["userInput"]["anyOf"] = new_any_of
        new_enum = copy.deepcopy(workflow_step_user_input.specification["inputOptions"])
        new_enum.append(None)
        response_schema["properties"]["userInput"]["enum"] = new_enum

    return response_schema

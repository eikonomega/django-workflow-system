"""Response Schema Generator Module for a Multiple Choice Question"""
import copy
import itertools
from itertools import permutations
from django_workflow_system.utils import RESPONSE_SCHEMA


def get_response_schema(workflow_step_user_input):
    """
    Build and returns a response schema for a given WorkflowStepUserInput w/
    a WorkflowStepUserInputType of 'Multiple Choice Question'.

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

        response_schema["properties"]["userInput"][
            "enum"
        ] = fetch_all_combinations_unordered(
            workflow_step_user_input.specification["correctInput"]
        )

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
        response_schema["properties"]["userInput"]["enum"] = fetch_all_combinations(
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
        new_enum = fetch_all_combinations(workflow_step_user_input)
        new_enum.append(None)
        response_schema["properties"]["userInput"]["enum"] = new_enum

    return response_schema


def fetch_all_combinations(workflow_step_user_input):
    """
    Fetch all possible combinations of a multi choice question.

    Args:
        workflow_step_user_input (WorkflowStepUserInput): The WorkflowStepUserInput Object.

    Returns:
        list: All possible combinations of available answers.
    """
    # We need to get the range of input options, loop through and create a monster
    all_combos = []
    for number in range(
        1, len(workflow_step_user_input.specification["inputOptions"]) + 1
    ):
        all_combos += [
            list(combo)
            for combo in itertools.combinations(
                workflow_step_user_input.specification["inputOptions"], number
            )
        ]
    return all_combos


def fetch_all_combinations_unordered(correct_answer):
    """
    Fetch all possible combinations of a multi choice question, where order does not matter.

    Args:
        workflow_step_user_input (WorkflowStepUserInput): The Workflow correct input.

    Returns:
        list: All possible combinations of available answers.
    """

    all_combos = []
    combos = []
    combos = permutations(correct_answer)
    for i in combos:
        all_combos += [list(i)]
    return all_combos

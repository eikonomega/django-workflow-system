"""Response Schema Generator Module for a Multiple Choice Question."""
import copy
import itertools

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

    # Scenario 1 They need to respond with the correct answer.
    if (
        workflow_step_user_input.specification["meta"]["inputRequired"]
        and workflow_step_user_input.specification["meta"]["correctInputRequired"]
    ):
        # Answer must be an array.
        response_schema["properties"]["userInput"]["type"] = "array"

        response_schema["properties"]["userInput"][
            "enum"
        ] = correct_answer_combinations(
            workflow_step_user_input.specification["correctInput"]
        )

    # Scenario 2: They need to answer, but not necessarily correctly.
    elif (
        workflow_step_user_input.specification["meta"]["inputRequired"]
        and not workflow_step_user_input.specification["meta"]["correctInputRequired"]
    ):
        # Answer must be an array.
        response_schema["properties"]["userInput"]["type"] = "array"

        # Get all possible combinations of input options.
        response_schema["properties"]["userInput"]["enum"] = all_possible_combinations(
            workflow_step_user_input.specification["inputOptions"]
        )

    # Scenario 3: Answer is not required and correct is not required, so null should be an option in potential responses
    else:
        response_schema["properties"]["userInput"]["type"] = ["array", "null"]

        new_enum = all_possible_combinations(
            workflow_step_user_input.specification["inputOptions"]
        )
        new_enum.append(None)
        response_schema["properties"]["userInput"]["enum"] = new_enum

    return response_schema


def all_possible_combinations(input_options):
    """
    Determine all possible combinations for a given set of input options.

    Args:
        input_options: A list of options.
    """
    all_combos = []
    for number_of_selected_answers in range(len(input_options)):
        for potential_combination in itertools.permutations(
            input_options, number_of_selected_answers + 1
        ):
            all_combos.append(list(potential_combination))

    return all_combos


def correct_answer_combinations(correct_answer):
    """
    Determine all possible orderings for the "correct answers" to a multi choice question.

    Args:
        correct_answer: An array who elements comprised the correct answer to the question.
    """

    combos = itertools.permutations(correct_answer)
    all_combos = [list(combo) for combo in combos]

    return all_combos

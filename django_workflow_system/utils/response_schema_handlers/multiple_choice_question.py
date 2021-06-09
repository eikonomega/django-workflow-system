"""Response Schema Generator Module for a Multiple Choice Question"""
import copy
import itertools

from django_workflow_system.utils import RESPONSE_SCHEMA


def get_response_schema(workflow_step_user_input):
    """
    Build and returns a response schema for a given WorkflowStepUserInput w/
    a WorkflowStepUserInputType of 'Multiple Choice Question'.
    """
    response_schema = copy.deepcopy(RESPONSE_SCHEMA)

    # Now we need to check some things.....
    if workflow_step_user_input.specification['meta']['inputRequired'] and workflow_step_user_input.specification['meta']['correctInputRequired']:
        # They need to respond with the correct answer.
        response_schema['properties']['userInput']['type'] = workflow_step_user_input.type.json_schema['properties']['correctInput']['type']
        response_schema['properties']['userInput']['enum'] = [
            workflow_step_user_input.specification['correctInput']]

    elif workflow_step_user_input.specification['meta']['inputRequired'] and not workflow_step_user_input.specification['meta']['correctInputRequired']:
        # They don't need to respond with the correct answer.
        response_schema['properties']['userInput']['type'] = workflow_step_user_input.type.json_schema['properties']['correctInput']['type']
        response_schema['properties']['userInput']['enum'] = fetch_all_combinations(
            workflow_step_user_input)

    else:
        # Answer is not required and correct is not required, so null should be an option in potential responses
        response_schema['properties']['userInput']['anyOf'] = [
            {"type": workflow_step_user_input.type.json_schema['properties']['correctInput']['type']}, {"type": 'null'}]
        new_enum = fetch_all_combinations(workflow_step_user_input)
        new_enum.append(None)
        response_schema['properties']['userInput']['enum'] = new_enum

    return response_schema


def fetch_all_combinations(workflow_step_user_input):
    """
    Fetch all possible combinations of a multi choice question.
    """
    # We need to get the range of input options, loop through and create a monster
    all_combos = []
    for number in range(1, len(workflow_step_user_input.specification['inputOptions']) + 1):
        all_combos += [list(combo) for combo in itertools.combinations(
            workflow_step_user_input.specification['inputOptions'], number)]
    return all_combos

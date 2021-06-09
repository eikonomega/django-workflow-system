"""Response Schema Generator Module for a Multiple Choice Question"""

import itertools


def get_response_schema(instance):
    """
    Build and returns a response schema for a given WorkflowStepUserInput w/
    a WorkflowStepUserInputType of 'Multiple Choice Question'.
    """
    response_schema = {
        "type": "object",
        "properties": {
            "stepInputID": {
                "type": "string",
                "format": "uuid"
            },
            "userInput": {}
        }
    }

    # Now we need to check some things.....
    if instance.specification['meta']['inputRequired'] and instance.specification['meta']['correctInputRequired']:
        # They need to respond with the correct answer.
        response_schema['properties']['userInput']['type'] = instance.type.json_schema['properties']['correctInput']['type']
        response_schema['properties']['userInput']['enum'] = [
            instance.specification['correctInput']]

    elif instance.specification['meta']['inputRequired'] and not instance.specification['meta']['correctInputRequired']:
        # They don't need to respond with the correct answer.
        response_schema['properties']['userInput']['type'] = instance.type.json_schema['properties']['correctInput']['type']
        response_schema['properties']['userInput']['enum'] = fetch_all_combinations(instance)

    else:
        # Answer is not required and correct is not required, so null should be an option in potential responses
        response_schema['properties']['userInput']['anyOf'] = [{"type": instance.type.json_schema['properties']['correctInput']['type']}, {"type": 'null'}]
        new_enum = fetch_all_combinations(instance)
        new_enum.append(None)
        response_schema['properties']['userInput']['enum'] = new_enum

    return response_schema


def fetch_all_combinations(instance):
    """
    Fetch all possible combinations of a multi choice question.
    """
    # We need to get the range of input options, loop through and create a monster
    all_combos = []
    for number in range(1, len(instance.specification['inputOptions']) + 1):
        all_combos += [list(combo) for combo in itertools.combinations(instance.specification['inputOptions'], number)]
    return all_combos

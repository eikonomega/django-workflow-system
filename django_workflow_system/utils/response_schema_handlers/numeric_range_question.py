"""Response Schema Generator Module for a Numeric Range Question"""



def get_response_schema(instance):
    """
    Build and returns a response schema for a given WorkflowStepUserInput w/
    a WorkflowStepUserInputType of 'Numeric Range Question'.
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
        response_schema['properties']['userInput']['enum'] = [instance.specification['correctInput']]

    elif instance.specification['meta']['inputRequired'] and not instance.specification['meta']['correctInputRequired']:
        # They don't need to respond with the correct answer.
        response_schema['properties']['userInput']['type'] = instance.type.json_schema['properties']['correctInput']['type']
        response_schema['properties']['userInput']['enum'] = fetch_numbers(instance)

    else:
        # Answer is not required and correct is not required, so null should be an option in potential responses
        response_schema['properties']['userInput']['anyOf'] = [{"type": instance.type.json_schema['properties']['correctInput']['type']}, {"type": 'null'}]
        new_enum = fetch_numbers(instance)
        new_enum.append(None)
        response_schema['properties']['userInput']['enum'] = new_enum

    return response_schema


def fetch_numbers(instance):
    """
    Loop through and create a list of all possible numbers.
    """
    number_list = []
    for number in range(instance.specification['inputOptions']['minimumValue'], instance.specification['inputOptions']['maximumValue'] + instance.specification['inputOptions']['step'], instance.specification['inputOptions']['step']):
        number_list.append(number)
    return number_list

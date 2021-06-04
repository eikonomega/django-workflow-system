

def get_response_schema(instance):
    """
    Build and returns a response schema for a given WorkflowStepUserInput w/
    a WorkflowStepUserInputType of 'Single Choice Question'.
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
        response_schema['properties']['userInput']['anyOf'] = instance.type.json_schema['properties']['correctInput']['anyOf']
        response_schema['properties']['userInput']['enum'] = [
            instance.specification['correctInput']]

    elif instance.specification['meta']['inputRequired'] and not instance.specification['meta']['correctInputRequired']:
        # They don't need to respond with the correct answer.
        response_schema['properties']['userInput']['anyOf'] = instance.type.json_schema['properties']['correctInput']['anyOf']

    elif not instance.specification['meta']['inputRequired'] and instance.specification['meta']['correctInputRequired']:
        # They need to respond with the correct answer.
        response_schema['properties']['userInput']['anyOf'] = instance.type.json_schema['properties']['correctInput']['anyOf']
        response_schema['properties']['userInput']['enum'] = [instance.specification['correctInput']]

    # If it doesn't need a response and doesn't need to be correct then I believe we can just leave this as an empty dict

    return response_schema

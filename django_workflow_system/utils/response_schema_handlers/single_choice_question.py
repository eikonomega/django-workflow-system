

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
        response_schema['properties']['userInput']['enum'] = instance.specification['inputOptions']

    else:
        # Answer is not required and correct is not required, so null should be an option in potential responses
        new_any_of = instance.type.json_schema['properties']['correctInput']['anyOf']
        new_any_of.append({"type": 'null'})
        response_schema['properties']['userInput']['anyOf'] = new_any_of
        new_enum = instance.specification['inputOptions']
        new_enum.append(None)
        response_schema['properties']['userInput']['enum'] = new_enum

    return response_schema

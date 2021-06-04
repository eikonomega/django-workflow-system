

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
        # We need to enumerate our options here.....
        da_enum = []
        for number in range(instance.specification['inputOptions']['minimumValue'], instance.specification['inputOptions']['maximumValue'] + instance.specification['inputOptions']['step'], instance.specification['inputOptions']['step']):
            da_enum.append(number)
        response_schema['properties']['userInput']['enum'] = da_enum

    elif not instance.specification['meta']['inputRequired'] and instance.specification['meta']['correctInputRequired']:
        # They need to respond with the correct answer.
        response_schema['properties']['userInput']['type'] = instance.type.json_schema['properties']['correctInput']['type']
        response_schema['properties']['userInput']['enum'] = [instance.specification['correctInput']]

    # If it doesn't need a response and doesn't need to be correct then I believe we can just leave userInput as an empty dict
    return response_schema

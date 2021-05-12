import json

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_protect

from django_workflow_system.models import WorkflowStepUserInputType


@csrf_protect
def get_user_input_type_helper(request):
    """
    Get information on whether the text message has been sent, or whether the
    user has successfully deactivated their UserTarget.
    """
    if request.GET.get('uuid', None):
        uuid = request.GET.get('uuid', None)
        user_input_type = WorkflowStepUserInputType.objects.get(id=uuid)
        payload = {
            "specification": user_input_type.placeholder_specification
        }

    else:
        payload = {}

    return HttpResponse(json.dumps(payload))
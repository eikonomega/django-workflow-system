import json

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_protect

from django_workflow_system.models import WorkflowStepUserInputType


@csrf_protect
def get_user_input_type_helper(request):
    """
    Get the example_specification of a given WorkflowStepUserInputType
    """
    if request.GET.get("uuid", None):
        uuid = request.GET.get("uuid", None)
        user_input_type = WorkflowStepUserInputType.objects.get(id=uuid)
        payload = {"specification": user_input_type.example_specification}

    else:
        payload = {}

    return HttpResponse(json.dumps(payload))

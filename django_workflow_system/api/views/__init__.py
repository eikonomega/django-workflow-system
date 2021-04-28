"""
SECURITY INFO
Default Authentication/Permission for API views are defined
in the settings files for your environment. Make sure that you are
aware of what is set there.

"""
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse

# from django_workflow_system.api.views.user.workflows import workflow_user_data_api_root


@api_view(["GET"])
def workflow_api_root(request, format=None):
    """Overview of available resources in this API."""
    return Response(
        {
            "workflows": reverse("workflows", request=request, format=format),
            "workflow-authors": reverse(
                "workflow-authors", request=request, format=format
            ),
            "workflow-collections": reverse(
                "workflow-collections", request=request, format=format
            ),
            "workflow-user-data": reverse(
                "workflow-user-data-root", request=request, format=format
            ),
        }
    )

from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404

from rest_framework import exceptions as drf_exceptions
from rest_framework.response import Response
from rest_framework.views import APIView

from ...serializers.workflows.workflow import (
    WorkflowSummarySerializer, WorkflowDetailedSerializer)
from ....models import Workflow


class WorkflowsView(APIView):
    """
    **Supported HTTP Methods**

    * Get: Retrieve all Workflows representations.

    Notes
    -----
    Workflows that are part of collections will not be displayed 
    via this endpoint. They are access via the collection detail endpoint.
    """

    required_scopes = ['read']

    def get(self, request):
        """
        Retrieve all Workflows.

        Returns:
            A JSON object representation of all Workflows.
            [
                {
                    "id": "3ec6f24c-a578-4a78-9d22-4e67354891ed",
                    "name": "Workflow III",
                    "detail": "http://localhost:8000/api_v3/workflows/workflows/3ec6f24c-a578-4a78-9d22-4e67354891ed/",
                    "author": {
                        "id": "13972dc1-aa03-443e-a67e-1bdfe4c1c617",
                        "user": {
                            "first_name": "Brett",
                            "last_name": "Fox"
                        },
                        "detail": "http://localhost:8000/api_v3/workflows/authors/13972dc1-aa03-443e-a67e-1bdfe4c1c617/",
                        "title": "Mr.",
                        "image": "http://localhost:8000/media/workflows/author/13972dc1-aa03-443e-a67e-1bdfe4c1c617/profileImage.png"
                    },
                    "image": "http://localhost:8000/media/workflows/3ec6f24c-a578-4a78-9d22-4e67354891ed/cover-image.jpg",
                }
            ]
        """
        # TODO: filter only latest version of each workflow,
        #  unless the user needs a previous version,
        #  then show that version
        workflows = Workflow.objects.all()

        serializer = WorkflowSummarySerializer(
            workflows, many=True, context={'request': request})
        return Response(serializer.data)


class WorkflowView(APIView):
    """
    **Supported HTTP Methods**

    * Get: Retrieve a specific Workflow representation.

    Notes
    -----
    Unlike the collection endpoint for this resource class, this endpoint
    will return information on any Workflow regardless of whether or not
    it is a member of a WorkflowCollection.
    """

    required_scopes = ['read']

    def get(self, request, id):
        """
        Retrieves a specific Workflow.

        Parameters:
            id (str): id of Workflow

        Returns:
            A JSON object representation of the Workflow resource.
            {
                "id": "6b6bfb2e-d227-4d0b-9141-1c8e9c29520a",
                "code": "BGA",
                "name": "Workflow I",
                "image": "http://localhost:8000/media/workflows/6b6bfb2e-d227-4d0b-9141-1c8e9c29520a/cover-image.png",
                "author": {
                    "id": "13972dc1-aa03-443e-a67e-1bdfe4c1c617",
                    "user": {
                        "first_name": "Brett",
                        "last_name": "Fox"
                    },
                    "detail": "http://localhost:8000/api_v3/workflows/authors/13972dc1-aa03-443e-a67e-1bdfe4c1c617/",
                    "title": "Mr.",
                    "image": "http://localhost:8000/media/workflows/author/13972dc1-aa03-443e-a67e-1bdfe4c1c617/profileImage.png"
                },
                "workflowstep_set": [
                    {
                        "code": "1000",
                        "order": 1,
                        "ui_template": "Cool Beans",
                        "workflowstepinput_set": [],
                        "workflowsteptext_set": [],
                        "workflowstepaudio_set": [],
                        "workflowstepimage_set": [],
                        "workflowstepvideo_set": []
                    }
                ]
            }

        Raises:
            drf_exceptions.NotFound
                When no Workflow resources exists for the given 'id'.

                404: Not Found
                {
                    "detail": "No Workflow with id: f06d37eb-da06-4b74-b7e5-3058e6c6e3ce."
                }
        """
        workflow = get_object_or_404(Workflow, id=id)
        serializer = WorkflowDetailedSerializer(
            workflow, context={'request': request})
        return Response(serializer.data)

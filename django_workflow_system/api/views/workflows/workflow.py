from django.shortcuts import get_object_or_404

from rest_framework.response import Response
from rest_framework.views import APIView

from ...serializers.workflows.workflow import (
    WorkflowSummarySerializer,
    WorkflowDetailedSerializer,
)
from ....models import Workflow


class WorkflowsView(APIView):
    """
    **Supported HTTP Methods**

    * Get: Retrieve all Workflows representations.

    Notes:
        Workflows that are part of collections will not be displayed
        via this endpoint. They are accessed via the collection detail endpoint.
    """

    required_scopes = ["read"]

    def get(self, request):
        """
        Retrieve all Workflows.

        Returns:
            A JSON object representation of all Workflows.
            [
                {
                    "id": "71689475-c779-4620-9623-dc5cbc0ec612",
                    "name": "Workflow_1",
                    "detail": "http://127.0.0.1:8000/workflow_system/workflows/71689475-c779-4620-9623-dc5cbc0ec612/",
                    "author": {
                        "id": "47d41a0c-e460-4ce4-8880-a9cf088cc818",
                        "user": {
                            "first_name": "Justin",
                            "last_name": "Branco"
                        },
                        "detail": "http://127.0.0.1:8000/workflow_system/authors/47d41a0c-e460-4ce4-8880-a9cf088cc818/",
                        "title": "Dr",
                    },
                    "images": [
                        {
                            "image_url": "workflows/8538dc36-3a6f-47e1-9132-14d070252b74/home.jpg",
                            "image_type": "home"
                        }
                    ],
                }
            ]
        """
        # TODO: filter only latest version of each workflow,
        #  unless the user needs a previous version,
        #  then show that version
        workflows = Workflow.objects.all()

        serializer = WorkflowSummarySerializer(
            workflows, many=True, context={"request": request}
        )
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

    required_scopes = ["read"]

    def get(self, request, id):
        """
        Retrieves a specific Workflow.

        Parameters:
            id (str): id of Workflow

        Returns:
            A JSON object representation of the Workflow resource.
            {
                "id": "71689475-c779-4620-9623-dc5cbc0ec612",
                "self_detail": "http://127.0.0.1:8000/workflow_system/workflows/71689475-c779-4620-9623-dc5cbc0ec612/",
                "code": "Workflow_1_Code",
                "name": "Workflow_1",
                "images": [
                    {
                        "image_url": "workflows/8538dc36-3a6f-47e1-9132-14d070252b74/home.jpg",
                        "image_type": "home"
                    }
                ],
                "author": {
                    "id": "47d41a0c-e460-4ce4-8880-a9cf088cc818",
                    "user": {
                        "first_name": "Justin",
                        "last_name": "Branco"
                    },
                    "detail": "http://127.0.0.1:8000/workflow_system/authors/47d41a0c-e460-4ce4-8880-a9cf088cc818/",
                    "title": "Dr",
                    "image": "http://127.0.0.1:8000/workflows/authors/47d41a0c-e460-4ce4-8880-a9cf088cc818/profileImage.png"
                },
                "workflowstep_set": [
                    {
                        "id": "cf33e6d9-6fd7-4a09-b59e-368ceb7ab675",
                        "code": "Workflow_1_Step_1",
                        "order": 1,
                        "ui_template": "Workflow_1_Step_1_Template",
                        "workflowstepuserinput_set": [
                            {
                                "id": "846173f7-6faf-4d12-9261-4f390bf03600",
                                "workflow_step": "cf33e6d9-6fd7-4a09-b59e-368ceb7ab675",
                                "ui_identifier": "Step 1 Input",
                                "required": true,
                                "response_schema": "655c8526-3bfa-402f-bf7c-48bf8b24f84b"
                            }
                        ],
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
        serializer = WorkflowDetailedSerializer(workflow, context={"request": request})
        return Response(serializer.data)

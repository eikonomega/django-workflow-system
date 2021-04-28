from django.shortcuts import get_object_or_404

from rest_framework.response import Response
from rest_framework.views import APIView

from ...serializers.workflows.author import (
    WorkflowAuthorSummarySerializer,
    WorkflowAuthorDetailedSerializer,
)
from ....models import WorkflowAuthor


class WorkflowAuthorsView(APIView):
    """
    **Supported HTTP Methods**

    * Get: Retrieve summary representations of all Workflow authors.
    """

    required_scopes = ["read"]

    def get(self, request):
        """
        Retrieve all Workflow Authors.

        Returns:
            A JSON object representation of all Workflow Authors.
            [
                {
                    "id": "47d41a0c-e460-4ce4-8880-a9cf088cc818",
                    "user": {
                        "first_name": "Justin",
                        "last_name": "Branco"
                    },
                    "detail": "http://127.0.0.1:8000/workflow_system/authors/47d41a0c-e460-4ce4-8880-a9cf088cc818/",
                    "title": "Dr",
                    "image": "http://127.0.0.1:8000/workflows/authors/47d41a0c-e460-4ce4-8880-a9cf088cc818/profileImage.png"
                }
            ]
        """
        serializer = WorkflowAuthorSummarySerializer(
            WorkflowAuthor.objects.all(), many=True, context={"request": request}
        )
        return Response(serializer.data)


class WorkflowAuthorView(APIView):
    """
    **Supported HTTP Methods**

    * Get: Retrieve a detailed representation of a specific Workflow Author.
    """

    required_scopes = ["read"]

    def get(self, request, id):
        """
        Retrieve specific Workflow Author.

        Path Parameters:
            id (str): UUID of Author

        Returns:
            A JSON object representation of the requested Workflow Author
            {
                "self_detail": "http://127.0.0.1:8000/workflow_system/authors/47d41a0c-e460-4ce4-8880-a9cf088cc818/",
                "id": "47d41a0c-e460-4ce4-8880-a9cf088cc818",
                "user": {
                    "first_name": "Justin",
                    "last_name": "Branco"
                },
                "title": "Dr",
                "image": "http://127.0.0.1:8000/workflows/authors/47d41a0c-e460-4ce4-8880-a9cf088cc818/profileImage.png",
                "biography": "After I became a Doctor I became an Admin!",
                "workflow_set": [
                    {
                        "name": "Workflow_1",
                        "detail": "http://127.0.0.1:8000/workflow_system/workflows/71689475-c779-4620-9623-dc5cbc0ec612/"
                    }
                ]
            }

        Raises:
            drf_exceptions.NotFound
                When no Author resource exists for the given `id`.

                404: Not Found
                {
                    "detail": "No Author with id: 5747129b-13d8-4d86-9230-1408fb6efd16."
                }
        """
        author = get_object_or_404(WorkflowAuthor, id=id)
        serializer = WorkflowAuthorDetailedSerializer(
            author, context={"request": request}
        )
        return Response(serializer.data)

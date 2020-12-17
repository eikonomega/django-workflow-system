from django.shortcuts import get_object_or_404

from rest_framework.response import Response
from rest_framework.views import APIView

from ...serializers.workflows.author import (
    WorkflowAuthorSummarySerializer, WorkflowAuthorDetailedSerializer)
from ....models import WorkflowAuthor


class WorkflowAuthorsView(APIView):
    """
    **Supported HTTP Methods**

    * Get: Retrieve summary representations of all Workflow authors.
    """
    required_scopes = ['read']

    def get(self, request):
        """
        Retrieve all Workflow Authors.

        Returns
        -------
            Response
                A JSON object representation of all Workflow Authors.

                [
                    {
                        "id": "f8987318-a445-4588-a7ac-5c0c385f6bd8",
                        "user": {
                            "first_name": "Steve",
                            "last_name": "Smith"
                        },
                        "detail": "http://127.0.0.1:8000/api_v3/workflow-authors/f8987318-a445-4588-a7ac-5c0c385f6bd8",
                        "title": "Dr",
                        "image": "http://127.0.0.1:8000/media/workflows/author/f8987318-a445-4588-a7ac-5c0c385f6bd8/profileImage.png"
                    }
                    ...
                ]

        """
        serializer = WorkflowAuthorSummarySerializer(
            WorkflowAuthor.objects.all(),
            many=True,
            context={'request': request})
        return Response(serializer.data)


class WorkflowAuthorView(APIView):
    """
    **Supported HTTP Methods**

    * Get: Retrieve a detailed representation of a specific Workflow Author.
    """

    required_scopes = ['read']

    def get(self, request, id):
        """
        Retrieve specific Workflow Author.

        Path Parameters
        ----------
            id: str
                UUID of Author

        Returns
        -------
            Response
                A JSON object representation of the requested Workflow Author
                {
                    "id": "f8987318-a445-4588-a7ac-5c0c385f6bd8",
                    "user": {
                        "first_name": "Steve",
                        "last_name": "Smith"
                    },
                    "title": "Dr",
                    "image": "http://127.0.0.1:8000/media/workflows/author/f8987318-a445-4588-a7ac-5c0c385f6bd8/profileImage.png",
                    "biography": "Stuff and things",
                    "workflow_set": [
                        {
                            "name": "Workflow I",
                            "detail": "http://127.0.0.1:8000/api_v3/workflows/0477a1dc-961b-4d06-9d19-92c85524db3e",
                            "image": "http://127.0.0.1:8000/media/workflow/0477a1dc-961b-4d06-9d19-92c85524db3e/coverImage.jpg"
                        }
                    ]
                }

        Raises
        -------
            drf_exceptions.NotFound
                When no Author resource exists for the given `id`.

                404: Not Found
                {
                    "detail": "No Author with id: 5747129b-13d8-4d86-9230-1408fb6efd16."
                }
        """
        author = get_object_or_404(WorkflowAuthor, id=id)
        serializer = WorkflowAuthorDetailedSerializer(
            author, context={'request': request})
        return Response(serializer.data)

from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status


from ...serializers.workflows.collection import (
    WorkflowCollectionSummarySerializer,
    WorkflowCollectionDetailedSerializer,
    WorkflowCollectionWithStepsSerializer,
)
from ....models import (
    WorkflowCollection,
    WorkflowCollectionAssignment,
    WorkflowCollectionSubscription,
)


class WorkflowCollectionsView(APIView):
    """
    **Supported HTTP Methods**

    * Get: Retrieve summary representations of (kind of) all Active Workflow Collections.
    Specifically, get will return each workflow collection the user has a connection to,
    be it through an assignment, engagement, or suggestion, PLUS the newest version of
    all remaining workflow collections.
    """

    required_scopes = ["read"]

    def get(self, request):
        """
        This method does NOT return all Active Workflow Collections.
        It specifically returns only the newest version of each workflow collection
        unless a user has an open assignment/engagement/suggestion with an earlier version
        of that workflow. It also returns deactivated versions for which the user is
        still "connected".

        Returns:
            A JSON object representation of all Active Workflow Collections.
            [
                {
                    "id": "c7b1940f-f19d-49ab-9ed5-7161dd185087",
                    "detail": "http://127.0.0.1:8000/workflow_system/collections/c7b1940f-f19d-49ab-9ed5-7161dd185087/",
                    "code": "c_1",
                    "version": 1,
                    "active": true,
                    "created_date": "2021-03-09T19:34:51.517701Z",
                    "modified_date": "2021-03-09T19:34:51.517728Z",
                    "description": "This is the first of many workflow collections.",
                    "assignment_only": false,
                    "recommendable": true,
                    "name": "Workflow_Collection_1",
                    "ordered": false,
                    "authors": [
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
                    ],
                    "images": [
                        {
                            "image_url": "workflows/collections/cd297706-adb3-43d7-bb81-dcf6d2a506d3/Detail.png",
                            "image_type": "Detail"
                        },
                        {
                            "image_url": "workflows/collections/ef37306b-0859-4fa0-9003-dd63968bda8b/Home.png",
                            "image_type": "Home"
                        }
                    ],
                    "category": "SURVEY",
                    "metadata": [
                        ["Breakfast", "Eggs", "Bacon"]
                    ],
                    "newer_version": null
                }
            ]
        """

        user = request.user
        if not user.username:
            return Response(
                data={"error": "Must be logged in."}, status=status.HTTP_400_BAD_REQUEST
            )
        now = timezone.now()

        # these three queries are used to determine which OLD versions the user should see.

        open_assignments = WorkflowCollectionAssignment.objects.filter(
            user=user,
            status__in=(
                WorkflowCollectionAssignment.ASSIGNED,
                WorkflowCollectionAssignment.IN_PROGRESS,
            ),
        )
        open_subscriptions = WorkflowCollectionSubscription.objects.filter(
            user=user,
            active=True,
        )

        old_bois = WorkflowCollection.objects.filter(
            Q(workflowcollectionassignment__in=open_assignments)
            | Q(workflowcollectionsubscription__in=open_subscriptions)
        )

        # add to old_bois all the newer workflow collections which are not newer
        # versions of any of the old bois
        old_names = {boi.code for boi in old_bois}
        new_bois = WorkflowCollection.objects.filter(active=True).exclude(
            code__in=old_names
        )

        all_bois = (old_bois | new_bois).distinct()

        serializer = WorkflowCollectionSummarySerializer(
            all_bois, many=True, context={"request": request}
        )
        return Response(serializer.data)


class WorkflowCollectionView(APIView):
    """
    **Supported HTTP Methods**

    * Get: Retrieve a detailed representation of a specific Active Workflow
    Collection.
    """

    required_scopes = ["read"]

    def get(self, request, id):
        """
        Retrieves a specific Active Workflow Collection.

        Path Parameters:
            id (str): id of Workflow Collection

        Query Parameters:
            include_steps (str): "True", "true", "False", or "false", indicating whether or not to
                                 include workflow steps. Defaults to false.

        Returns:
            A JSON object representation of a Active Workflow Collection resources.
            {
                "self_detail": "http://127.0.0.1:8000/workflow_system/collections/c7b1940f-f19d-49ab-9ed5-7161dd185087/",
                "id": "c7b1940f-f19d-49ab-9ed5-7161dd185087",
                "code": "c_1",
                "version": 1,
                "active": true,
                "created_date": "2021-03-09T19:34:51.517701Z",
                "modified_date": "2021-03-09T19:34:51.517728Z",
                "description": "This is the first of many workflow collections.",
                "assignment_only": false,
                "recommendable": true,
                "name": "Workflow_Collection_1",
                "ordered": false,
                "workflowcollectionmember_set": [
                    {
                        "order": 1,
                        "workflow": {
                            "name": "Workflow_1",
                            "detail": "http://127.0.0.1:8000/workflow_system/workflows/71689475-c779-4620-9623-dc5cbc0ec612/",
                            "image": "http://127.0.0.1:8000/workflows/workflows/71689475-c779-4620-9623-dc5cbc0ec612/cover-image.png"
                        }
                    }
                ],
                "authors": [
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
                ],
                "images": [
                    {
                        "image_url": "workflows/collections/cd297706-adb3-43d7-bb81-dcf6d2a506d3/Detail.png",
                        "image_type": "Detail"
                    },
                    {
                        "image_url": "workflows/collections/ef37306b-0859-4fa0-9003-dd63968bda8b/Home.png",
                        "image_type": "Home"
                    }
                ],
                "category": "SURVEY",
                "metadata": [
                        ["Breakfast", "Eggs", "Bacon"]
                ],
                "newer_version": null
            }

        Raises
            drf_exceptions.NotFound
                When no Workflow Collection resources exists for the given 'id'.

                404: Not Found
                {
                    "detail": "No Workflow Collection with id: 19ce5c1b-0f4e-430a-b3e8-b2a5dbb2a462."
                }
        """

        include_steps = request.query_params.get("include_steps", "False")
        if include_steps in ("True", "true"):
            include_steps = True
        elif include_steps in ("False", "false"):
            include_steps = False
        else:
            raise ValidationError(
                f"Invalid value for include_steps: {include_steps}", "invalid"
            )

        workflow_collection = get_object_or_404(WorkflowCollection, id=id)
        if include_steps:
            serializer = WorkflowCollectionWithStepsSerializer(
                workflow_collection, context={"request": request}
            )
        else:
            serializer = WorkflowCollectionDetailedSerializer(
                workflow_collection, context={"request": request}
            )
        return Response(serializer.data)

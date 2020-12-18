from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from ...serializers.workflows.collection import (
    WorkflowCollectionSummarySerializer,
    WorkflowCollectionDetailedSerializer, WorkflowCollectionWithStepsSerializer)
from ....models import (
    WorkflowCollection, WorkflowCollectionAssignment,
    WorkflowCollectionSubscription)


class WorkflowCollectionsView(APIView):
    """
    **Supported HTTP Methods**

    * Get: Retrieve summary representations of (kind of) all Active Workflow Collections.
    Specifically, get will return each workflow collection the user has a connection to,
    be it through an assignment, engagement, or suggestion, PLUST the newest version of
    all remaining workflow collections.
    """
    required_scopes = ['read']

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
                    "id": "644a7970-f50a-4df6-8928-68dafc2e6ead",
                    "detail": "http://localhost:8000/api_v3/workflows/collections/644a7970-f50a-4df6-8928-68dafc2e6ead/",
                    "code": "123",
                    "detail_image": "http://localhost:8000/media/collection/644a7970-f50a-4df6-8928-68dafc2e6ead/detail-image.png",
                    "home_image": "http://localhost:8000/media/collection/644a7970-f50a-4df6-8928-68dafc712893d/home-image.png",
                    "library_image": "http://localhost:8000/media/collection/644a7970-f50a-4df6-8928-lom09pLas/library-image.png",
                    "assignment_only": true,
                    "name": "Collection I",
                    "ordered": true,
                    "authors": [
                        {
                            "id": "13972dc1-aa03-443e-a67e-1bdfe4c1c617",
                            "user": {
                                "first_name": "Brett",
                                "last_name": "Fox"
                            },
                            "detail": "http://localhost:8000/api_v3/workflows/authors/13972dc1-aa03-443e-a67e-1bdfe4c1c617/",
                            "title": "Mr.",
                            "image": "http://localhost:8000/media/workflows/author/13972dc1-aa03-443e-a67e-1bdfe4c1c617/profileImage.png"
                        },
                        {
                            "id": "8a3f55f2-7138-4c3a-9d4b-aeb8a11f0ccf",
                            "user": {
                                "first_name": "Justin",
                                "last_name": "Branco"
                            },
                            "detail": "http://localhost:8000/api_v3/workflows/authors/8a3f55f2-7138-4c3a-9d4b-aeb8a11f0ccf/",
                            "title": "Sir",
                            "image": "http://localhost:8000/media/workflows/author/8a3f55f2-7138-4c3a-9d4b-aeb8a11f0ccf/profileImage.png"
                        }
                    ],
                    "category": "SURVEY",
                },
                {
                    "id": "b08e618e-0146-4723-b326-a2a9d97ff409",
                    "detail": "http://localhost:8000/api_v3/workflows/collections/b08e618e-0146-4723-b326-a2a9d97ff409/",
                    "code": "LMT",
                    "detail_image": "http://localhost:8000/media/collection/644a7970-f50a-4df6-8928-68dafc2e6ead/detail-image.png",
                    "home_image": "http://localhost:8000/media/collection/644a7970-f50a-4df6-8928-68dafc712893d/home-image.png",
                    "library_image": "http://localhost:8000/media/collection/644a7970-f50a-4df6-8928-lom09pLas/library-image.png",
                    "assignment_only": false,
                    "name": "Collection III",
                    "ordered": false,
                    "authors": [
                        {
                            "id": "13972dc1-aa03-443e-a67e-1bdfe4c1c617",
                            "user": {
                                "first_name": "Brett",
                                "last_name": "Fox"
                            },
                            "detail": "http://localhost:8000/api_v3/workflows/authors/13972dc1-aa03-443e-a67e-1bdfe4c1c617/",
                            "title": "Mr.",
                            "image": "http://localhost:8000/media/workflows/author/13972dc1-aa03-443e-a67e-1bdfe4c1c617/profileImage.png"
                        }
                    ],
                    "category": "SURVEY",
                }
            ]
        """

        user = request.user
        now = timezone.now()

        # these three queries are used to determine which OLD versions the user should see.

        open_assignments = WorkflowCollectionAssignment.objects.filter(
            user=user,
            status__in=(
                WorkflowCollectionAssignment.ASSIGNED,
                WorkflowCollectionAssignment.IN_PROGRESS
            )
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
            all_bois, many=True, context={'request': request})
        return Response(serializer.data)


class WorkflowCollectionView(APIView):
    """
    **Supported HTTP Methods**

    * Get: Retrieve a detailed representation of a specific Active Workflow
    Collection.
    """

    required_scopes = ['read']

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
                "id": "644a7970-f50a-4df6-8928-68dafc2e6ead",
                "code": "123",
                "detail_image": "http://localhost:8000/media/collection/644a7970-f50a-4df6-8928-68dafc2e6ead/detail-image.png",
                "home_image": "http://localhost:8000/media/collection/644a7970-f50a-4df6-8928-68dafc712893d/home-image.png",
                "library_image": "http://localhost:8000/media/collection/644a7970-f50a-4df6-8928-lom09pLas/library-image.png",
                "assignment_only": true,
                "name": "Collection I",
                "ordered": true,
                "workflowcollectionmember_set": [
                    {
                        "order": 2,
                        "workflow": {
                            "name": "Workflow I",
                            "detail": "http://localhost:8000/api_v3/workflows/workflows/6b6bfb2e-d227-4d0b-9141-1c8e9c29520a/"
                        }
                    },
                    {
                        "order": 1,
                        "workflow": {
                            "name": "Workflow II",
                            "detail": "http://localhost:8000/api_v3/workflows/workflows/7ce2913b-4960-476e-b622-71eae0244f78/"
                        }
                    }
                ],
                "authors": [
                    {
                        "id": "13972dc1-aa03-443e-a67e-1bdfe4c1c617",
                        "user": {
                            "first_name": "Brett",
                            "last_name": "Fox"
                        },
                        "detail": "http://localhost:8000/api_v3/workflows/authors/13972dc1-aa03-443e-a67e-1bdfe4c1c617/",
                        "title": "Mr.",
                        "image": "http://localhost:8000/media/workflows/author/13972dc1-aa03-443e-a67e-1bdfe4c1c617/profileImage.png"
                    },
                    {
                        "id": "8a3f55f2-7138-4c3a-9d4b-aeb8a11f0ccf",
                        "user": {
                            "first_name": "Justin",
                            "last_name": "Branco"
                        },
                        "detail": "http://localhost:8000/api_v3/workflows/authors/8a3f55f2-7138-4c3a-9d4b-aeb8a11f0ccf/",
                        "title": "Sir",
                        "image": "http://localhost:8000/media/workflows/author/8a3f55f2-7138-4c3a-9d4b-aeb8a11f0ccf/profileImage.png"
                    }
                ],
                "category": "SURVEY",
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
            raise ValidationError(f"Invalid value for include_steps: {include_steps}", "invalid")

        workflow_collection = get_object_or_404(WorkflowCollection, id=id)
        if include_steps:
            serializer = WorkflowCollectionWithStepsSerializer(
                workflow_collection, context={'request': request})
        else:
            serializer = WorkflowCollectionDetailedSerializer(
                workflow_collection, context={'request': request})
        return Response(serializer.data)

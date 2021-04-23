"""DRF View Definition."""
import logging

from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from .....models import WorkflowCollectionRecommendation
from ....serializers.user.workflows.recommendation import (
    WorkflowCollectionRecommendationSerializer,
)
from .....utils.logging_utils import generate_extra

logger = logging.getLogger(__name__)


class WorkflowCollectionRecommendationsView(APIView):
    """
    **Supported HTTP Methods**

    * Get: Retrieve summary representations of all current Workflow Collection Recommendations for the user

    * Post: Create a new Workflow Collection Recommendation

    """

    required_scopes = ["read", "write"]

    def get(self, request):
        """
        GET all WorkflowCollectionRecommendation resources for the current user

        Returns
        -------
            A HTTP response containing a list-like JSON representation
            of the user's workflow collection recommendations.
        [
            {
                "workflow_collection": "https://localhost/api_v3/workflows/collections/91a321ae-2a0a-4a49-b209-133437dda7a1/",
                "start": "2019-12-06T17:17:40.827557-05:00",
                "end": null
            }
        ]
        """
        serializer = WorkflowCollectionRecommendationSerializer(
            WorkflowCollectionRecommendation.objects.filter(
                start__lte=timezone.now()
            ).filter(
                Q(end__isnull=True) or Q(end__gt=timezone.now()),
                user=request.user,
            ),
            many=True,
            context={"request": request},
        )
        return Response(serializer.data)

    def post(self, request):
        """

        Body Parameters
        ----------
        workflow_collection: UUID
            the UUID of the Recommended WorkflowCollection
        start: datetime
            the start time for when the recommendation is valid
        end: datetime or None
            the end time for when the recommedation is valid

        Returns
        -------
        {
            'detail': 'http://testserver/api_v3/users/self/workflows/recommendations/872b9ddc-32b6-4340-a131-b92ab4c2a306/',
            'workflow_collection': 'http://testserver/api_v3/workflows/collections/72d7d60f-1e1c-4583-b2b7-8a357a9fccca/',
            'start': '2020-06-01T16:51:20.679049-04:00',
            'end': None
        }
        """
        serializer = WorkflowCollectionRecommendationSerializer(
            data=request.data,
            context={"request": request},
        )

        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as e:
            logger.error(
                "Error validating Workflow Collection Recomendation",
                exc_info=e,
                extra=generate_extra(
                    request=request,
                    serializer_errors=serializer.errors,
                ),
            )
            raise e
        else:
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)


class WorkflowCollectionRecommendationView(APIView):
    """
    **Supported HTTP Methods**

    * Get: Get a particular WorkflowCollectionRecommendation resource
      belonging to the requesting user.

    * Patch: Update a particular WorkflowCollectionRecommendation resource
      belonging to the requesting user.

    """

    required_scopes = ["read", "write"]

    def get(self, request, id):
        """

        Parameters
        ----------
        id: UUID
            the UUID of the requested WorkflowCollectionRecommendation

        Returns
        -------
        {
            'detail': 'http://testserver/api_v3/users/self/workflows/recommendations/872b9ddc-32b6-4340-a131-b92ab4c2a306/',
            'workflow_collection': 'http://testserver/api_v3/workflows/collections/72d7d60f-1e1c-4583-b2b7-8a357a9fccca/',
            'start': '2020-06-01T16:51:20.679049-04:00',
            'end': None
        }

        """
        workflow_collection_recommendation = get_object_or_404(
            WorkflowCollectionRecommendation,
            id=id,
            user=request.user,
        )

        serializer = WorkflowCollectionRecommendationSerializer(
            workflow_collection_recommendation,
            context={"request": request},
        )

        return Response(data=serializer.data)

    def patch(self, request, id):
        """

        Body Parameters
        ----------
        workflow_collection: UUID
            the UUID of the Recommended WorkflowCollection
        start: datetime
            the start time for when the recommendation is valid. Defaults to now.
        end: datetime or None
            the end time for when the recommedation is valid. Defaults to None, which signifies forever.

        Returns
        -------
        {
            'detail': 'http://testserver/api_v3/users/self/workflows/recommendations/872b9ddc-32b6-4340-a131-b92ab4c2a306/',
            'workflow_collection': 'http://testserver/api_v3/workflows/collections/72d7d60f-1e1c-4583-b2b7-8a357a9fccca/',
            'start': '2020-06-01T16:51:20.679049-04:00',
            'end': None
        }
        """

        workflow_collection_recommendation = get_object_or_404(
            WorkflowCollectionRecommendation,
            id=id,
            user=request.user,
        )

        serializer = WorkflowCollectionRecommendationSerializer(
            workflow_collection_recommendation,
            data=request.data,
            context={"request": request},
            partial=True,
        )

        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as e:
            logger.error(
                "Validation Error",
                exc_info=e,
                extra=generate_extra(
                    request=request,
                    workflow_collection_recommendation=workflow_collection_recommendation,
                    serializer_errors=serializer.errors,
                ),
            )
            raise e
        else:
            serializer.save()
            return Response(data=serializer.data)

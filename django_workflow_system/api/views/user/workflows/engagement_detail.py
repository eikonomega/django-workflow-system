"""DRF View Definition."""
import logging

from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import status
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from .....models import WorkflowCollectionEngagement, WorkflowCollectionEngagementDetail
from ....serializers.user.workflows.engagement import (
    WorkflowCollectionEngagementBaseSerializer,
)
from ....serializers.user.workflows.engagement_detail import (
    WorkflowCollectionEngagementDetailSerializer,
)
from .....utils.logging_utils import generate_extra


logger = logging.getLogger(__name__)


class WorkflowCollectionEngagementDetailsView(APIView):
    """
    **Supported HTTP Methods**

    * Get: Retrieve summary representations of all WorkflowCollectionEngagementDetails
      for a given WorkflowEngagement belonging to the requesting user.
    * Post: Create a new WorkflowCollectionEngagementDetail resource for a
      given WorkflowEngagement on behalf of the requesting user.
    """

    required_scopes = ["read", "write"]

    def get(self, request, id):
        """
        Retrieve WorkflowCollectionEngagementDetail representations
        associated with a given WorkflowEngagement for current user.

        Path Parameters:
            id (str): The UUID of the WorkflowEngagement to retrieve details on.

        Returns:
            A HTTP response containing a list-like JSON representation
            of the subscription with a 200 status code.
            [
                {
                    "detail": "http://127.0.0.1:8000/workflow_system/users/self/workflows/engagements/9b264dd6-0e53-4c39-9473-2d0888405532/details/e41fe4ec-5a12-4c6f-aef9-d4848dd1ee62/",
                    "step": "cf33e6d9-6fd7-4a09-b59e-368ceb7ab675",
                    "user_responses": {
                        "example_response": "this is the response"
                    },
                    "started": "2021-03-09T21:06:57Z",
                    "finished": null
                }
            ]

        """
        engagement_details = WorkflowCollectionEngagementDetail.objects.filter(
            workflow_collection_engagement=id,
            workflow_collection_engagement__user=request.user,
        )

        serializer = WorkflowCollectionEngagementDetailSerializer(
            engagement_details, context={"request": request}, many=True
        )

        return Response(data=serializer.data)

    def post(self, request, id):
        """
        Create a WorkflowCollectionEngagementDetail resource.

        Path Parameters:
            id (str): The UUID of the WorkflowEngagement for which to create
                      a new WorkflowCollectionEngagementDetail resource.

        Body Parameters:
            workflow_collection_engagement (foreign key): The WorkflowCollectionEngagement object
                                                          associated with the engagement detail.
            step (foreign key): The WorkflowStep associated with the engagement detail.
            user_responses (dict): Internal representation of JSON response from user.
            started (datetime): The start date of the engagement detail.
            finished (datetime): The finish date of the engagement detail.

        Returns:
            A HTTP response containing a list-like JSON representation
            of the subscription with a 201 status code
            AND the engagement state which includes the previous and next steps.

            {
                'detail': 'http://testserver/api_v3/users/self/workflows/engagements/3e26ae35-046c-45c7-bf1c-7245e96f0942/details/e608aaee-4d44-434e-b20d-7446b3ec7be6/',
                'step': UUID('9acd8aac-b535-4a78-b332-1c30a2f75b8d'),
                'user_responses': None,
                'started': '2019-09-13T10:20:00.081316-04:00',
                'finished': None,
                'state': {
                    'next_workflow': 'http://testserver/api_v3/workflows/workflows/401eaf82-6117-4580-9cd0-e5a9df62f490/',
                    'next_step_id': UUID('9acd8aac-b535-4a78-b332-1c30a2f75b8d'),
                    'prev_workflow': None,
                    'prev_step_id': None,
                    'previously_completed_workflows': []
                }
            }


        Raises:
            400: bad request
            {
                "step": [
                    "Not a valid uuid."
                ],
            }

            409: duplicate resource
            {
                "duplicate_resource": "An existing resource conflicts with the specified data."
            }
        """

        # The workflow_collection_engagement attribute needed by the serializer
        # is captured in the URL route. Injecting it into the payload here.
        request.data["workflow_collection_engagement"] = id
        # We need to set a submitted time on the input
        if "user_responses" in request.data.keys() and request.data["user_responses"]:
            request.data["user_responses"][-1]["submittedTime"] = str(timezone.now())

        serializer = WorkflowCollectionEngagementDetailSerializer(
            data=request.data, context={"request": request}
        )

        try:
            serializer.is_valid(raise_exception=True)
        except DRFValidationError as e:
            logger.error(
                "Error validating Workflow Collection Engagement Detail",
                exc_info=e,
                extra=generate_extra(
                    request=request,
                    serializer_errors=serializer.errors,
                ),
            )

            # Handle uniqueness constraint violation
            if (
                "non_field_errors" in serializer.errors
                and serializer.errors["non_field_errors"][0].code == "unique"
            ):

                return Response(
                    data={"detail": serializer.errors["non_field_errors"][0]},
                    status=status.HTTP_409_CONFLICT,
                )
            raise e
        else:
            serializer.save()

            # In order for UI clients to know what action to take after
            # a user POSTs a new step completion via this endpoint, we
            # need to return the updated `state` property of the enclosing
            # WorkflowCollectionEngagement object.

            engagement = WorkflowCollectionEngagement.objects.get(
                id=request.data["workflow_collection_engagement"]
            )

            engagement_serializer = WorkflowCollectionEngagementBaseSerializer(
                instance=engagement,
                context={"request": request},
            )
            data = serializer.data
            data["state"] = engagement_serializer.data["state"]

            # Check if we are able to proceed to the next step
            if data["user_responses"] and "inputs" in data["user_responses"][-1].keys():

                are_answers_valid = []

                for entry in serializer.data["user_responses"][-1]["inputs"]:
                    try:
                        are_answers_valid.append(entry["is_valid"])
                    except KeyError as exception:
                        print("Exception Encountered: ", exception)
                        print("Entry: ", entry)

                data["state"]["proceed"] = False if False in are_answers_valid else True
            else:
                data["state"]["proceed"] = True

            return Response(data=data, status=status.HTTP_201_CREATED)


class WorkflowCollectionEngagementDetailView(APIView):
    """
    READ/UPDATE operations for a single WorkflowCollectionEngagementDetail resource.

    **Supported HTTP Methods**

    * Get: Retrieve a detailed representation of a specific
      WorkflowCollectionEngagementDetail resource associated with a given
      WorkflowEngagement and belonging to the requesting user.

    * Patch: Update a specific WorkflowCollectionEngagementDetail resource
      associated with a given WorkflowEngagement and belonging
      to the requesting user.
    """

    required_scopes = ["read", "write"]

    def get(self, request, engagement_id, id):
        """
        Retrieve a WorkflowCollectionEngagementDetail representation for current user.

        Path Parameters:
            engagement_id (str): The UUID of the WorkflowEngagement that the
                                 WorkflowCollectionEngagementDetail belongs to.
            id (str): The UUID of the WorkflowCollectionEngagementDetail to retrieve.

        Notes:
            The `engagement_id` parameter is not actually used, but is
            passed in because of the URL route structure.

        Returns:
            A HTTP response containing a dict-like JSON representation
            of the resource with a 200 status code.

            {
                "detail": "http://127.0.0.1:8000/workflow_system/users/self/workflows/engagements/9b264dd6-0e53-4c39-9473-2d0888405532/details/e41fe4ec-5a12-4c6f-aef9-d4848dd1ee62/",
                "step": "cf33e6d9-6fd7-4a09-b59e-368ceb7ab675",
                "user_responses": {
                    "example_response": "this is the response"
                },
                "started": "2021-03-09T21:06:57Z",
                "finished": null
            }

        Raises:
            drf_exceptions.NotFound
                If the specified resource cannot be found or is not
                accessible by the requesting user.

                {
                    "detail": "No matching Workflow Engagement Detail found."
                }
        """

        engagement_detail = get_object_or_404(
            WorkflowCollectionEngagementDetail,
            id=id,
            workflow_collection_engagement__user=request.user,
        )

        serializer = WorkflowCollectionEngagementDetailSerializer(
            engagement_detail, context={"request": request}
        )

        return Response(data=serializer.data)

    def patch(self, request, engagement_id, id):
        """
        Update a WorkflowUserEngagementDetail resource for the current user.

        Path Parameters:
            id (str): The UUID of the workflow user engagement detail to modify.

        Body Parameters:
            step (foreign key): The WorkflowStep associated with the engagement detail.
            user_responses (dict): Internal representation of JSON response from user.
            started (datetime): The start date of the engagement detail.
            finished (datetime): The finish date of the engagement detail.

        Returns:
            A HTTP response object that depending on the result
            of the operation will have varying status codes and payloads.
            {
                "detail": "http://127.0.0.1:8000/workflow_system/users/self/workflows/engagements/9b264dd6-0e53-4c39-9473-2d0888405532/details/e41fe4ec-5a12-4c6f-aef9-d4848dd1ee62/",
                "step": "cf33e6d9-6fd7-4a09-b59e-368ceb7ab675",
                "user_responses": {
                    "example_response": "this is the response patched"
                },
                "started": "2021-03-09T21:06:57Z",
                "finished": null,
                "state": {
                    "next_step_id": "cf33e6d9-6fd7-4a09-b59e-368ceb7ab675",
                    "prev_step_id": null,
                    "steps_completed_in_collection": 0,
                    "steps_in_collection": 1,
                    "steps_completed_in_workflow": 0,
                    "steps_in_workflow": 1,
                    "previously_completed_workflows": [],
                    "next_workflow": "http://127.0.0.1:8000/workflow_system/workflows/71689475-c779-4620-9623-dc5cbc0ec612/",
                    "prev_workflow": null
                },
                "proceed": true
            }

        Raises:
            drf_exceptions.NotFound
                If no resource exists for the provided `id`.

                {
                    "detail": "No matching user engagement found."
                }

            drf_exceptions.PermissionDenied
                If requesting user doesn't own the requested resource.
                This is translated by DRF into an HTTP response object.

                {
                    "detail": "You do not have permission to perform this action."
                }
        """
        engagement_detail = get_object_or_404(
            WorkflowCollectionEngagementDetail,
            id=id,
            workflow_collection_engagement__user=request.user,
        )

        # We need to set a submitted time on the input
        if "user_responses" in request.data.keys() and request.data["user_responses"]:
            request.data["user_responses"][-1]["submittedTime"] = str(timezone.now())

        serializer = WorkflowCollectionEngagementDetailSerializer(
            engagement_detail,
            data=request.data,
            partial=True,
            context={"request": request},
        )

        try:
            serializer.is_valid(raise_exception=True)
        except DRFValidationError as e:
            logger.error(
                "Error validating Engagement Detail",
                exc_info=e,
                extra=generate_extra(
                    request=request,
                    workflow_collection_engagement_detail=engagement_detail,
                    serializer_errors=serializer.errors,
                ),
            )
            raise e
        else:
            serializer.save()

            # In order for UI clients to know what action to take after
            # a user has updated an EngagementDetail via this endpoint, we
            # need to return the updated `state` property of the enclosing
            # WorkflowCollectionEngagement object.

            engagement = engagement_detail.workflow_collection_engagement
            engagement_serializer = WorkflowCollectionEngagementBaseSerializer(
                instance=engagement,
                context={"request": request},
            )
            data = serializer.data
            data["state"] = engagement_serializer.data["state"]

            # Check if we are able to proceed to the next step
            if data["user_responses"] and "inputs" in data["user_responses"][-1].keys():

                are_answers_valid = []

                for entry in serializer.data["user_responses"][-1]["inputs"]:
                    try:
                        are_answers_valid.append(entry["is_valid"])
                    except KeyError as exception:
                        print("Exception Encountered: ", exception)
                        print("Entry: ", entry)

                data["state"]["proceed"] = False if False in are_answers_valid else True
            else:
                data["state"]["proceed"] = True

            return Response(data=data, status=status.HTTP_200_OK)

from dateutil import parser as datetimeparser
import logging
import uuid

from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.exceptions import ValidationError, ErrorDetail
from rest_framework.response import Response
from rest_framework.views import APIView

from .....utils.logging_utils import generate_extra
from .....models import (
    WorkflowCollectionEngagement, WorkflowCollection)
from ....serializers.user.workflows.engagement import (
    WorkflowCollectionEngagementDetailedSerializer,
    WorkflowCollectionEngagementSummarySerializer, WorkflowCollectionEngagementAndDetailsSerializer)


logger = logging.getLogger(__name__)


class WorkflowCollectionEngagementsView(APIView):
    """
    **Supported HTTP Methods**

    * Get: Retrieve summary representations of all "non-finished" Workflow Collection
           Engagements for the user.
    * Post: Create a new Workflow Collection Engagement the requesting user.
    """

    required_scopes = ['read', 'write']

    def get(self, request):
        """
        GET all WorkflowCollectionEngagement resources for current user

        Parameters:
        start (optional datetime): lower bound for start time of engagements. defaults to None
        end (optional datetime): upper bound for start time of engagements. defaults to None
        include_finished (optional bool): defaults to false for compatibility reasons
        collection_id (optional uuid): uuid of the collection for which to retrieve engagements
        include_details (optional bool): whether or not to include engagement details, using the 
                                         detailed serializer

        Returns:
            A HTTP response containing a list-like JSON representation
            of the subscription with a 200 status code.

            [
                {
                    'detail': 'http://testserver/api_v3/users/self/workflows/engagements/f1ef2ed0-6e42-4f55-a09f-c46a51058914/',
                    'workflow_collection': 'http://testserver/api_v3/workflows/collections/038141f6-6117-493a-b3bc-4eee6754d5f4/',
                    'started': '2019-11-12T11:10:13.776766-05:00',
                    'finished': None,
                    'state': {
                        'next_step_id': UUID('1d6972ee-29f7-49c6-9aed-3395aa406651'),
                        'prev_step_id': None,
                        'steps_completed_in_collection': 0,
                        'steps_in_collection': 3,
                        'steps_completed_in_workflow': 0,
                        'steps_in_workflow': 3,
                        'previously_completed_workflows': [],
                        'next_workflow': 'http://testserver/api_v3/workflows/workflows/eeb3b02e-daa9-40f8-8091-edcf9e3d55d1/',
                        'prev_workflow': None
                    }
                }
            ]
        """
        ### Validation ###
        start = request.query_params.get('start', None)
        end = request.query_params.get('end', None)
        include_finished = request.query_params.get("include_finished", False)
        include_details = request.query_params.get("include_details", False)
        collection_id = request.query_params.get("collection_id", None)
        errors = {}
        if start:
            try:
                start = datetimeparser.isoparse(start)
            except ValueError:
                errors["start"] = [ErrorDetail("Invalid datetime", "invalid")]
                start = None
        if end:
            try:
                end = datetimeparser.isoparse(end)
            except ValueError:
                errors["end"] = [ErrorDetail("Invalid datetime", "invalid")]
                end = None

        if start and end and start > end:
            errors["non_field_errors"] = [ErrorDetail("Invalid Start and End time order", "invalid")]

        if include_finished not in (True, False, "true", "True", "false", "False"):
            errors["include_finished"] = [ErrorDetail("Invalid value")]

        if include_details not in (True, False, "true", "True", "false", "False"):
            errors["include_details"] = [ErrorDetail("Invalid value")]

        if collection_id:
            try:
                uuid.UUID(collection_id)
            except ValueError:
                errors["collection_id"] = [ErrorDetail("Badly formed UUID")]
            else:
                if not WorkflowCollection.objects.filter(pk=collection_id):
                    errors["collection_id"] = [ErrorDetail("No workflow collection with matching ID found")]

        if errors:
            return Response(data=dict(errors), status=status.HTTP_400_BAD_REQUEST)

        ### Evaluating query ###
        engagements = WorkflowCollectionEngagement.objects.filter(user=request.user)

        if start:
            engagements = engagements.filter(started__gte=start)
        if end:
            engagements = engagements.filter(started__lt=end)
        if include_finished in (False, "false", "False"):
            engagements = engagements.filter(finished=None)
        if collection_id:
            engagements = engagements.filter(workflow_collection__id=collection_id)

        if include_details in (True, "True", "true"):
            serializer = WorkflowCollectionEngagementAndDetailsSerializer(
                engagements,
                many=True,
                context={'request': request})
        else:
            serializer = WorkflowCollectionEngagementSummarySerializer(
                engagements,
                many=True,
                context={'request': request})

        return Response(data=serializer.data)

    def post(self, request):
        """
        Create new WorkflowCollectionEngagement resource for the requesting
        user.

        Body Parameters:
            workflow (foreign key): The Workflow object associated with the engagement.
            user (foreign key): The User object who is engaging the Workflow.
            started (datetime): The start date for the engagement.
            finished (datetime): The finish date for the engagement.

        Returns:
            if successful: A JSON representation of all Engagement
            resources for the requesting user.

            {
                'self_detail': 'http://testserver/api_v3/users/self/workflows/engagements/a01dfbee-61bd-4548-b160-5de262675237/',
                'workflow_collection': 'http://testserver/api_v3/workflows/collections/028d645b-b527-4d7a-8b2d-04fb65573d31/',
                'started': '2019-11-12T10:58:54.205653-05:00',
                'finished': None,
                'workflowcollectionengagementdetail_set': [],
                'state': {
                    'next_step_id': UUID('abb16ec0-435e-42a2-b43c-a9aaa4c752e6'),
                    'prev_step_id': None,
                    'steps_completed_in_collection': 0,
                    'steps_in_collection': 3,
                    'steps_completed_in_workflow': 0,
                    'steps_in_workflow': 3,
                    'previously_completed_workflows': [],
                    'next_workflow': 'http://testserver/api_v3/workflows/workflows/040cee2c-6e3a-445d-bc94-b460c385a459/',
                    'prev_workflow': None
                }
            }

        Raises:
            400: bad request
            {
                "detail": "No workflow engagement found with that id."
            }
            409: engagement already exists
            {
                "duplicate_resource": "An existing resource conflicts with the specified data."
            }
        """
        serializer = WorkflowCollectionEngagementDetailedSerializer(
            data=request.data, context={'request': request})

        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as e:
            logger.error(
                "Error validating Workflow Collection Engagement",
                exc_info=e,
                extra=generate_extra(
                    request=request,
                    serializer_errors=serializer.errors,
                )
            )

            # Handling if resource is an attempt of a duplicate engagement
            if ('non_field_errors' in serializer.errors and
                    serializer.errors['non_field_errors'][0].code == 'unique') or \
                ('non_field_errors' in serializer.errors and
                 serializer.errors['non_field_errors'][0] == (
                    'The user has an existing incomplete engagement for this workflow collection.')):

                return Response(
                    data={
                        'detail': serializer.errors['non_field_errors'][0]},
                    status=status.HTTP_409_CONFLICT)
            raise e
        else:
            instance: WorkflowCollectionEngagement = serializer.save()

            if instance.finished:
                logger.info(
                    "User '%s' completed workflow collection '%s' version '%d'",
                    request.user.username,
                    instance.workflow_collection.code,
                    instance.workflow_collection.version,
                    extra=generate_extra(
                        event_code="WORKFLOW_COLLECTION_ENGAGEMENT_COMPLETED",
                        request=request,
                        workflow_collection_engagement=instance,
                    )
                )

            return Response(serializer.data, status=status.HTTP_201_CREATED)


class WorkflowCollectionEngagementView(APIView):
    """
    **Supported HTTP Methods**

    * Get: Retrieve a detailed representation of a specific Workflow 
      Engagement owned by the requesting user.
    * Patch: Modifying an existing Workflow Engagement resource owned by
      the requesting user.
    """

    required_scopes = ['read', 'write']

    def get(self, request, id):
        """
        GET a WorkflowCollectionEngagement representation for current user.

        Path Parameters:
            id (str): The UUID of the WorkflowCollectionEngagement to retrieve.

        Returns:
            A HTTP response containing a dict-like JSON representation
            of the engagement target with a 200 status code.

            {
                "workflow_collection": "http://localhost:8000/api_v3/workflows/collections/db4029ae-9ff3-4f85-8129-69f85a3ba6ea/",
                "started": "2019-01-16T09:29:47-05:00",
                "finished": null,
                "workflowcollectionengagementdetail_set": [
                    {
                            "detail": "http://localhost:8000/api_v3/users/self/workflows/engagements/2b3fca55-a802-4b0f-b0df-215a17aac652/details/9b6240f7-a3ca-4c16-98ec-7c6ada508c72/",
                            "step": "95a14611-1993-41e6-8464-4fd69aa4a028",
                            "user_response": null,
                            "started": "2019-01-07T06:00:00-05:00",
                            "finished": null
                    }
                ]
            }

        Raises:
            drf_exceptions.NotFound
                If the request WorkflowCollectionEngagement cannot be found
                or isn't accessible for the requesting user.

                {
                    "detail": "No matching user engagement for current user."
                }
        """

        user_engagement = get_object_or_404(
            WorkflowCollectionEngagement, id=id, user=request.user
        )

        serializer = WorkflowCollectionEngagementDetailedSerializer(
            user_engagement, context={'request': request}
        )

        return Response(data=serializer.data)

    def patch(self, request, id):
        """
        PATCH Workflow User Engagement details update for current user.

        Path Parameters:
            id (str): The UUID of the workflow user engagement target to modify.

        Body Parameters:
            workflow_collection (foreign key): The Workflow Collection object associated with the 
                                               engagement.
            user (foreign key): The User object who is engaging the Workflow.
            started (datetime): The start date for the engagement.
            finished (datetime): The finish date for the engagement.

        Returns:
            A HTTP response object that depending on the result
            of the operation will have varying status codes and payloads.

            {
                "workflow_collection": "http://localhost:8000/api_v3/workflows/collections/db4029ae-9ff3-4f85-8129-69f85a3ba6ea/",
                "started": "2019-01-16T09:29:47-05:00",
                "finished": null,
                "workflowcollectionengagementdetail_set": [
                    {
                        "detail": "http://localhost:8000/api_v3/users/self/workflows/engagements/2b3fca55-a802-4b0f-b0df-215a17aac652/details/9b6240f7-a3ca-4c16-98ec-7c6ada508c72/",
                        "step": "95a14611-1993-41e6-8464-4fd69aa4a028",
                        "user_response": null,
                        "started": "2019-01-07T06:00:00-05:00",
                        "finished": null
                    }
                ]
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

        user_engagement = get_object_or_404(
            WorkflowCollectionEngagement, id=id, user=request.user
        )
        originally_unfinished = not user_engagement.finished

        serializer = WorkflowCollectionEngagementDetailedSerializer(
            user_engagement,
            data=request.data,
            partial=True,
            context={'request': request})

        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as e:
            logger.error(
                "Error validating Workflow Collection Engagement",
                exc_info=e,
                extra=generate_extra(
                    request=request,
                    workflow_collection_engagement=user_engagement,
                    serializer_errors=serializer.errors,
                )
            )
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            instance: WorkflowCollectionEngagement = serializer.save()
            if instance.finished and originally_unfinished:
                logger.info(
                    "User '%s' completed workflow collection '%s' version '%d'",
                    request.user.username,
                    instance.workflow_collection.code,
                    instance.workflow_collection.version,
                    extra=generate_extra(
                        event_code="WORKFLOW_COLLECTION_ENGAGEMENT_COMPLETED",
                        request=request,
                        workflow_collection_engagement=instance,
                    )
                )
            return Response(serializer.data)

from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils import timezone

from rest_framework import exceptions as drf_exceptions, status
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from .....utils.logging_utils import generate_extra
from ....serializers.user.workflows.assignment import (
    WorkflowCollectionAssignmentSummarySerializer,
)
from .....models import WorkflowCollectionAssignment

import logging

logger = logging.getLogger(__name__)


class WorkflowCollectionAssignmentsView(APIView):
    """
    **Supported HTTP Methods**

    * Get: Retrieve summary representations of all Workflow Collection Assignments for the user.
    """

    required_scopes = ["read"]

    def get(self, request):
        """
        Retrieve all Workflow Collection Assignments for the current user.

        Returns:
            A list-like JSON representation of all Workflow
            Collection Assignments for the requesting user.
            [
                {
                    "id": "f9ddca6b-513b-4436-b6e3-cd2c51c6458a",
                    "workflow_collection": "http://127.0.0.1:8000/workflow_system/collections/c7b1940f-f19d-49ab-9ed5-7161dd185087/",
                    "detail": "http://127.0.0.1:8000/workflow_system/users/self/workflows/assignments/f9ddca6b-513b-4436-b6e3-cd2c51c6458a/",
                    "engagement": null,
                    "start": "2021-03-09 09:00:00",
                    "status": "ASSIGNED"
                }
            ]
        """
        user_assignments = WorkflowCollectionAssignment.objects.filter(
            Q(user=request.user),
            Q(status=WorkflowCollectionAssignment.ASSIGNED)
            | Q(status=WorkflowCollectionAssignment.IN_PROGRESS),
        )

        serializer = WorkflowCollectionAssignmentSummarySerializer(
            user_assignments, many=True, context={"request": request}
        )

        return Response(data=serializer.data)


class WorkflowCollectionAssignmentView(APIView):
    """
    **Supported HTTP Methods**

    * Get: Retrieve a summary representation of a specific Workflow Collection Assignment for the user.
    * Patch: Update a specific Workflow Collection Assignment owned by the requesting user.
    """

    required_scopes = ["read", "write"]

    def user_workflow_collection_assignment(self, request, id):
        """
        Retrieve a WorkflowCollectionAssignment.

        Path Parameters:
            id (str): The UUID of the WorkflowCollectionAssignment resource to retrieve

        Returns:
            WorkflowCollectionAssignment

        Raises:
            drf_exceptions.NotFound: If no corresponding WorkflowCollectionAssignment resource exists.
        """
        try:
            return WorkflowCollectionAssignment.objects.get(id=id, user=request.user)
        except (WorkflowCollectionAssignment.DoesNotExist, ValidationError):
            raise drf_exceptions.NotFound(detail="No matching user assignment found.")

    def get(self, request, id):
        """
        Retrieve user's WorkflowCollectionAssignment representation.

        Path Parameters:
            id (str): The UUID of the WorkflowCollectionAssignment to retrieve.

        Returns:
            A HTTP response containing a dict-like JSON representation
            of the notification target with a 200 status code.
            {
                "id": "f9ddca6b-513b-4436-b6e3-cd2c51c6458a",
                "workflow_collection": "http://127.0.0.1:8000/workflow_system/collections/c7b1940f-f19d-49ab-9ed5-7161dd185087/",
                "detail": "http://127.0.0.1:8000/workflow_system/users/self/workflows/assignments/f9ddca6b-513b-4436-b6e3-cd2c51c6458a/",
                "engagement": null,
                "start": "2021-03-09 09:00:00",
                "status": "ASSIGNED"
            }

        Raises:
            drf_exceptions.NotFound:
                If the id given does not corresponded to a
                WorkflowCollectionAsssignment that is owned by the
                requesting user.
                {
                    "detail": "No matching user assignment found."
                }
        """
        serializer = WorkflowCollectionAssignmentSummarySerializer(
            self.user_workflow_collection_assignment(request, id),
            context={"request": request},
        )

        return Response(data=serializer.data)

    def patch(self, request, id):
        """
        Update a user WorkflowCollectionAssignment resource.

        Path Parameters:
            id (str): The UUID of the Workflow Collection Assignment to modify.

        Body Parameters:
            workflow_collection (foreign key): The WorkflowCollection object associated with the Assignment.
            user (foreign key): The User being assigned the Workflow.
            start (datetime): The datetime of the Assignment.
            status (charfield): Whether the assignment is active, stale, or complete

        Returns:
            A HTTP response object that depending on the result
            of the operation will have varying status codes and payloads.

            {
                "id": "8b03d086-14ba-4616-a8cf-dbf308f6e38b",
                "workflow_collection": "c971e924-3898-4304-bb0a-2d903669faeb",
                "detail": "http://localhost:8000/api_v3/users/self/workflows/assignments/8b03d086-14ba-4616-a8cf-dbf308f6e38b/",
                "engagement": "http://localhost:8000/api_v3/users/self/workflows/engagements/270e8ad2-cabb-4623-a047-32a40e6ee640/",
                "start": "2019-02-06 09:00:00",
                "status": "IN_PROGRESS"
            }

        Raises:
            drf_exceptions.NotFound
                If the id given does not corresponded to a
                WorkflowCollectionAssignment that is owned by the
                requesting user.
                {
                    "detail": "No matching user assignment found."
                }

        drf_exceptions.ValidationError
                If the payload fails serializer validation.
                {
                    "status": [
                        "\"MOSTLY_ACTIVE\" is not a valid choice."
                    ]
                }
        """

        assignment = self.user_workflow_collection_assignment(request, id)
        old_status = assignment.status
        serializer = WorkflowCollectionAssignmentSummarySerializer(
            assignment,
            data=request.data,
            partial=True,
            context={"request": request},
        )

        try:
            serializer.is_valid(raise_exception=True)
        except DRFValidationError as e:
            logger.error(
                "Error validating Workflow Collection Assignment",
                exc_info=e,
                extra=generate_extra(
                    request=request,
                    workflow_collection_assignment=serializer.instance,
                    serializer_errors=serializer.errors,
                ),
            )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            instance: WorkflowCollectionAssignment = serializer.save()

            new_status = instance.status
            if (
                old_status != new_status
                and new_status == WorkflowCollectionAssignment.CLOSED_COMPLETE
            ):
                logger.info(
                    "Assigment of collection %s to user %s is now CLOSED_COMPLETE",
                    instance.workflow_collection.code,
                    instance.user,
                    extra=generate_extra(
                        event_code="WORKFLOW_COLLECTION_ASSIGNMENT_COMPLETED",
                        workflow_collection_assignment=instance,
                    ),
                )

                if not instance.engagement.finished:
                    instance.engagement.finished = timezone.now()
                    instance.engagement.save()

            return Response(serializer.data)

import logging

from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from ....utils import convert_to_utc_time
from .....models import WorkflowCollectionSubscription
from .....utils.logging_utils import generate_extra
from ....serializers.user.workflows.subscription import (
    WorkflowCollectionSubscriptionSummarySerializer,
)

logger = logging.getLogger(__name__)


class WorkflowCollectionSubscriptionsView(APIView):
    """
    **Supported HTTP Methods**

    * Get: Retrieve summary representations of all
    WorkflowCollectionSubscriptions
      belonging to the requesting user.
    * Post: Create a new WorkflowCollectionSubscription resource
      for the requesting user.
    """

    required_scopes = ["read", "write"]

    def get(self, request):
        """
        Return all Workflow Collection Subscriptions for the current user.

        Returns:
            A HTTP response containing an array JSON representation
            of the subscriptions with a 200 status code.
            [
                {
                    "detail": "http://127.0.0.1:8000/workflow_system/users/self/workflows/subscriptions/ef78f851-78f1-4a2d-a81a-4382f2438ab2/",
                    "workflow_collection": "http://127.0.0.1:8000/workflow_system/collections/c7b1940f-f19d-49ab-9ed5-7161dd185087/",
                    "active": true,
                    "workflowcollectionsubscriptionschedule_set": [
                        {
                            "time_of_day": "19:37:13",
                            "day_of_week": 1,
                            "weekly_interval": 1
                        }
                    ]
                }
            ]
        """
        serializer = WorkflowCollectionSubscriptionSummarySerializer(
            WorkflowCollectionSubscription.objects.filter(user=request.user),
            many=True,
            context={"request": request},
        )

        return Response(data=serializer.data)

    def post(self, request):
        """
        Create new WorkflowCollectionSubscription for the requesting user.

        Body Parameters:
            workflow_collection (foreign key): The Workflow object associated with the subscription.
            active (boolean): Whether or not the subscription is active
            workflowcollectionsubscription_set (dict): The ability to set a workflow schedule.
                                                       Required fields: 'time_of_day'(timefield),
                                                       'day_of_week'(int),
                                                       'weekly_interval'(int)

        Returns:
            if successful: A JSON representation of all Subscription
            for the requesting user.
            {
                "detail": "http://127.0.0.1:8000/workflow_system/users/self/workflows/subscriptions/ef78f851-78f1-4a2d-a81a-4382f2438ab2/",
                "workflow_collection": "http://127.0.0.1:8000/workflow_system/collections/c7b1940f-f19d-49ab-9ed5-7161dd185087/",
                "active": true,
                "workflowcollectionsubscriptionschedule_set": [
                    {
                        "time_of_day": "19:37:13",
                        "day_of_week": 1,
                        "weekly_interval": 1
                    }
                ]
            }

        Raises:
            400: bad request
            {
                "detail": "No matching workflow collection
                subscriptions found."
            }
        """
        serializer = WorkflowCollectionSubscriptionSummarySerializer(
            data=request.data, context={"request": request}
        )

        try:
            workflow_subscriptions = request.data[
                "workflowcollectionsubscriptionschedule_set"
            ]
        except KeyError:
            # If a schedule isn't passed through, we'll skip this part
            pass
        else:
            for schedule_set in workflow_subscriptions:
                # This try/except is converting the time that is being passed in
                # from the mobile app into UTC time.
                try:
                    schedule_set["time_of_day"] = convert_to_utc_time(
                        schedule_set["time_of_day"], "%H:%M:%S%z"
                    )
                except ValueError:
                    # If there is no offset specified, we want to use the time
                    # that was passed in
                    pass

        try:
            serializer.is_valid(raise_exception=True)

        except ValidationError as e:
            logger.error(
                "Error Validating Workflow Collection Subscription",
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
            instance: WorkflowCollectionSubscription = serializer.save()
            logger.info(
                "User '%s' subscribed to workflow collection '%s'",
                request.user,
                instance.workflow_collection,
                extra=generate_extra(
                    event_code="WORKFLOW_COLLECTION_SUBSCRIPTION_CREATED",
                    user=request.user,
                    workflow_collection=instance.workflow_collection,
                    workflow_collection_subscription__active=instance.active,
                ),
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)


class WorkflowCollectionSubscriptionView(APIView):
    """
    **Supported HTTP Methods**

    * Get: Retrieve a summary representation of a particular
      WorkflowCollectionSubscription resource belonging to the requesting user.
    * Put: Update a particular WorkflowCollectionSubscription resource
      belonging to the requesting user.

    """

    required_scopes = ["read", "write"]

    def get(self, request, id):
        """
        Retrieve a WorkflowCollectionSubscription representation.

        Path Parameters:
            id (str): The UUID of the workflow collection subscription to retrieve.

        Returns:
            A HTTP response containing a dict-like JSON representation
            of the workflow collection subscription with a 200 status code.

            {
                "detail": "http://localhost:8000/api_v3/users/self/workflows/subscriptions/d13a664e-b976-4b48-ad55-b774fab87853/",
                "workflow_collection": "http://localhost:8000/api_v3/workflows/collections/d98d61f1-ebde-44b6-880d-d8913a344e0d/",
                "active": true,
                "workflowcollectionsubscriptionschedule_set": [
                    {
                        "time_of_day": "14:37:29",
                        "day_of_week": 3,
                        "weekly_interval": 1
                    }
                ]
            }


        Raises:
            drf_exceptions.NotFound
            {
                "detail": "No matching workflow collection subscriptions found."
            }
        """

        workflow_collection_subscription = get_object_or_404(
            WorkflowCollectionSubscription,
            id=id,
            user=request.user.id,
        )

        serializer = WorkflowCollectionSubscriptionSummarySerializer(
            workflow_collection_subscription, context={"request": request}
        )

        return Response(data=serializer.data)

    def put(self, request, id):
        """
        Update a WorkflowCollectionSubscription and associated WorkflowCollectionSubscriptionSchedule
        resources owned by the requesting user.

        Path Parameters:
            id (str): The UUID of the user subscription to modify.

        Body Parameters:
            workflow_collection (foreign key): The Workflow Collection object associated with the
                                               subscription.
            active (boolean): Whether or not the subscription is active
            workflowcollectionsubscription_set (array): The ability to set a workflow collection schedule.
                                                        Required fields: 'time_of_day'(timefield),
                                                        'day_of_week'(int),
                                                        'weekly_interval'(int)
        Returns:
            A HTTP response containing a dict-like JSON representation
            of the subscription with a 200 status code.

            {
                "detail": "http://localhost:8000/api_v3/users/self/workflows/collection/subscriptions/c13e6da1-664f-479f-9e2c-d05a5e147b88/",
                "workflow_collection": "http://localhost:8000/api_v3/workflows/collections/2b341c94-2cc9-4fa7-8b5a-9683f2f8be7c/",
                "active": true,
                "workflowcollectionsubscriptionschedule_set": [
                    {
                        "time_of_day": "14:53:12",
                        "day_of_week": 1,
                        "weekly_interval": 1
                    }
                ]
            }

        Raises:
            drf_exceptions.ValidationError
                If the payload fails serializer validation.

                {
                    "active": [
                        "Not a valid boolean."
                    ]
                }
        """

        workflow_collection_subscription = get_object_or_404(
            WorkflowCollectionSubscription,
            id=id,
            user=request.user,
        )

        serializer = WorkflowCollectionSubscriptionSummarySerializer(
            workflow_collection_subscription,
            data=request.data,
            context={"request": request},
        )

        try:
            workflow_subscriptions = request.data[
                "workflowcollectionsubscriptionschedule_set"
            ]
        except KeyError:
            # If a schedule isn't passed through, we'll skip this part
            pass
        else:
            for schedule_set in workflow_subscriptions:
                # This try/except is converting the time that is being passed in
                # from the mobile app into UTC time.
                try:
                    schedule_set["time_of_day"] = convert_to_utc_time(
                        schedule_set["time_of_day"], "%H:%M:%S%z"
                    )
                except ValueError:
                    # If there is no offset specified, we want to use the time
                    # that was passed in
                    pass
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as e:
            logger.error(
                "Validation error",
                exc_info=e,
                extra=generate_extra(
                    request=request,
                    workflow_collection_subscription=workflow_collection_subscription,
                    serializer_error=serializer.errors,
                ),
            )
            raise e
        else:
            instance = serializer.save()
            logger.info(
                "User '%s' updated their subscription to workflow collection '%s'",
                request.user,
                instance.workflow_collection,
                extra=generate_extra(
                    event_code="WORKFLOW_COLLECTION_SUBSCRIPTION_UPDATED",
                    user=request.user,
                    workflow_collection=instance.workflow_collection,
                    workflow_collection_subscription__active=instance.active,
                ),
            )
            return Response(serializer.data)

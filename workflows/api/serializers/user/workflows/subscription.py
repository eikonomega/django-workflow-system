"""DRF Serialzier Definition."""
from rest_framework import serializers, exceptions as drf_exceptions

from .....models import (
    WorkflowCollectionSubscription,
    WorkflowCollectionSubscriptionSchedule,
    WorkflowCollection,
)


class WorkflowCollectionSubscriptionScheduleSummarySerializer(
    serializers.ModelSerializer
):
    """Model Serializer for Workflow Collection Subscription Schedule Objects."""

    class Meta:
        model = WorkflowCollectionSubscriptionSchedule
        fields = ["time_of_day", "day_of_week", "weekly_interval"]


class WorkflowCollectionSubscriptionSummarySerializer(serializers.ModelSerializer):
    """ModelSerializer for Workflow Collection Subscription Objects."""

    detail = serializers.HyperlinkedIdentityField(
        view_name="user-workflow-collection-subscription", lookup_field="id"
    )

    workflow_collection = serializers.HyperlinkedRelatedField(
        queryset=WorkflowCollection.objects.all(),
        view_name="workflow-collection",
        lookup_field="id",
    )

    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    workflowcollectionsubscriptionschedule_set = (
        WorkflowCollectionSubscriptionScheduleSummarySerializer(many=True)
    )

    class Meta:
        model = WorkflowCollectionSubscription
        fields = [
            "detail",
            "workflow_collection",
            "user",
            "active",
            "workflowcollectionsubscriptionschedule_set",
        ]

    def create(self, validated_data):
        """
        Override create() method to be able to handle nested
        WorkflowCollectionSubscriptionSchedule object creations.
        """
        workflow_collection_subscription = (
            WorkflowCollectionSubscription.objects.create(
                user=validated_data["user"],
                active=validated_data["active"]
                if validated_data.get("active")
                else True,
                workflow_collection=validated_data["workflow_collection"],
            )
        )

        workflowcollectionsubscriptionschedule_data = validated_data.pop(
            "workflowcollectionsubscriptionschedule_set"
        )

        # TODO: This doesn't handle a user submitting multiple schedules for the same day.
        # Should raise an appropriate validation error.
        for subscription in workflowcollectionsubscriptionschedule_data:
            subscription[
                "workflow_collection_subscription"
            ] = workflow_collection_subscription
            WorkflowCollectionSubscriptionSchedule.objects.create(**subscription)

        return workflow_collection_subscription

    def update(self, instance, validated_data):
        """
        Update WorkflowCollectionSubscription and WorkflowCollectionSubscriptionSchedule objects.

        Notes:
            We only allow the user to update the "active" property of an
            existing WorkflowCollectionSubscription object or the related
            WorkflowCollectionSubscriptionSchedule objects. They cannot modify
            other aspects of the original WorkflowCollectionSubscription object.

        Parameters:
            instance (WorkflowCollectionSubscription): The object retrieved by DRF based on the URL
                                                       route being accessed by the user.
            validated_data (dict): A dictionary containing the parsed/validated data from
                                   the incoming HTTP request payload.

        Returns:
            WorkflowCollectionSubscription
                The modified WorkflowCollectionSubscription object.

        """
        instance.workflowcollectionsubscriptionschedule_set.all().delete()

        instance.active = validated_data["active"]

        workflowcollectionsubscriptionschedule_data = validated_data.pop(
            "workflowcollectionsubscriptionschedule_set"
        )

        # TODO: This doesn't handle a user submitting multiple schedules for the same day.
        # Should raise an appropriate validation error.
        for subscription in workflowcollectionsubscriptionschedule_data:
            subscription["workflow_collection_subscription"] = instance
            WorkflowCollectionSubscriptionSchedule.objects.create(**subscription)

        instance.save()
        return instance

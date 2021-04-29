"""DRF Serialzier Definition."""
from rest_framework import serializers

from .....models import (
    WorkflowCollectionEngagement,
    WorkflowCollectionAssignment,
    WorkflowCollection,
)


class WorkflowCollectionAssignmentSummarySerializer(serializers.ModelSerializer):
    """ModelSerializer for operations on multiple WorkflowAssignment objects."""

    detail = serializers.HyperlinkedIdentityField(
        view_name="user-workflow-assignment", lookup_field="id"
    )

    engagement = serializers.HyperlinkedRelatedField(
        queryset=WorkflowCollectionEngagement.objects.all(),
        view_name="user-workflow-collection-engagement",
        lookup_field="id",
        allow_null=True,
    )

    workflow_collection = serializers.HyperlinkedRelatedField(
        queryset=WorkflowCollection.objects.all(),
        view_name="workflow-collection",
        lookup_field="id",
    )

    class Meta:
        model = WorkflowCollectionAssignment
        fields = (
            "id",
            "workflow_collection",
            "detail",
            "engagement",
            "start",
            "status",
        )

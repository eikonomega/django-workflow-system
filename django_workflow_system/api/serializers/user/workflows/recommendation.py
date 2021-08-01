"""DRF Serializer Definition"""
from rest_framework import serializers

from .....models import (
    WorkflowCollection,
    WorkflowCollectionRecommendation,
)


class WorkflowCollectionRecommendationSerializer(serializers.ModelSerializer):
    """Serializer for WorkflowCollectionRecommendation objects"""

    detail = serializers.HyperlinkedIdentityField(
        view_name="user-workflow-recommendation", lookup_field="id"
    )
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    workflow_collection = serializers.HyperlinkedRelatedField(
        queryset=WorkflowCollection.objects.all(),
        view_name="workflow-collection",
        lookup_field="id",
    )

    class Meta:
        model = WorkflowCollectionRecommendation
        fields = [
            "detail",
            "user",
            "workflow_collection",
            "start",
            "end",
        ]

    def validate(self, data):
        def getattr_patched(attr_name):
            """
            This utility function retrieves 'attr_name' from data if it is present,
            otherwise it uses the value from self.instance. This is necessary because
            data will not have entries for all the fields in the Model
            if a partial update (PATCH) is performed.
            """
            if attr_name in data:
                return data[attr_name]
            if self.instance and hasattr(self.instance, attr_name):
                return getattr(self.instance, attr_name)
            return None

        start = getattr_patched("start")
        end = getattr_patched("end")
        if start and end and (end < start):
            raise serializers.ValidationError("start is less than end")

        return data

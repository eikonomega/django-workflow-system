from django.contrib.auth import get_user_model

from rest_framework import serializers

from ....models import Workflow, WorkflowAuthor


User = get_user_model()


class UserTerseSerializer(serializers.ModelSerializer):
    """
    Terse level serializer for Django User objects.
    """

    class Meta:
        model = User
        fields = ("first_name", "last_name")


# TODO: I can see why this is here to avoid a circular dependency. But I think we should fine a way to locate it with the other workflow serializers.
class WorkflowForeignKeyAuthorSummarySerializer(serializers.ModelSerializer):
    """
    Summary level serializer for Workflow objects.
    """

    detail = serializers.HyperlinkedIdentityField(
        view_name="workflow", lookup_field="id"
    )

    class Meta:
        model = Workflow
        fields = ["name", "detail"]


class WorkflowAuthorSummarySerializer(serializers.ModelSerializer):
    """
    Summary level serializer for WorkflowAuthor objects.
    """

    detail = serializers.HyperlinkedIdentityField(
        view_name="workflow-author", lookup_field="id"
    )

    user = UserTerseSerializer()

    class Meta:
        model = WorkflowAuthor
        fields = ("id", "user", "detail", "title", "image")


class WorkflowAuthorDetailedSerializer(serializers.ModelSerializer):
    """
    Detailed level serializer for WorkflowAuthor objects.
    """

    user = UserTerseSerializer()

    workflow_set = WorkflowForeignKeyAuthorSummarySerializer(many=True)

    self_detail = serializers.HyperlinkedIdentityField(
        view_name="workflow-author", lookup_field="id"
    )

    class Meta:
        model = WorkflowAuthor
        fields = (
            "self_detail",
            "id",
            "user",
            "title",
            "image",
            "biography",
            "workflow_set",
        )

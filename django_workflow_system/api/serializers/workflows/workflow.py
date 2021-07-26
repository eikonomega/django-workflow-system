from rest_framework import serializers

from .author import WorkflowAuthorSummarySerializer
from .step import WorkflowStepSerializer
from ..utils import get_images_helper
from ....models import Workflow


class WorkflowTerseSerializer(serializers.ModelSerializer):
    """
    Terse level serializer for Workflow objects.
    """

    detail = serializers.HyperlinkedIdentityField(
        view_name="workflow", lookup_field="id"
    )

    class Meta:
        model = Workflow
        fields = ("name", "detail")


class WorkflowSummarySerializer(serializers.ModelSerializer):
    """
    Summary level serializer for Workflow objects.
    """

    detail = serializers.HyperlinkedIdentityField(
        view_name="workflow", lookup_field="id"
    )

    author = WorkflowAuthorSummarySerializer()
    images = serializers.SerializerMethodField()
    metadata = serializers.SerializerMethodField()

    class Meta:
        model = Workflow
        fields = ("id", "name", "detail", "images", "author", "metadata")

    def get_images(self, instance):
        """
        Method to build an object for each corresponding Image.

        Parameters:
            instance (Workflow object)

        Returns:
            List of Image objects in JSON format.

        """
        return get_images_helper(
            self.context.get("request"), instance.workflowimage_set.all()
        )

    def get_metadata(self, instance):
        """
        Helper method for gathering collection metadata

        Parameters:
        instance : WorkflowCollection object

        Returns:
            List of Lists of Metadata associated with the Collection
        """
        metadata_list = []
        for hierarchy in instance.metadata.all():
            metadata_list.append(hierarchy.group_hierarchy)

        return metadata_list


class WorkflowDetailedSerializer(serializers.ModelSerializer):
    """
    Detailed level serializer for Workflow objects.
    """

    author = WorkflowAuthorSummarySerializer()
    workflowstep_set = WorkflowStepSerializer(many=True)
    self_detail = serializers.HyperlinkedIdentityField(
        view_name="workflow", lookup_field="id"
    )
    images = serializers.SerializerMethodField()
    metadata = serializers.SerializerMethodField()

    class Meta:
        model = Workflow
        fields = (
            "id",
            "self_detail",
            "code",
            "name",
            "author",
            "images",
            "workflowstep_set",
            "metadata",
        )

    def get_images(self, instance):
        """
        Method to build an object for each corresponding Image.

        Parameters:
            instance (Workflow object)

        Returns:
            List of Image objects in JSON format.

        """
        return get_images_helper(
            self.context.get("request"), instance.workflowimage_set.all()
        )

    def get_metadata(self, instance):
        """
        Helper method for gathering collection metadata

        Parameters:
        instance : WorkflowCollection object

        Returns:
            List of Lists of Metadata associated with the Collection
        """
        metadata_list = []
        for hierarchy in instance.metadata.all():
            metadata_list.append(hierarchy.group_hierarchy)

        return metadata_list


class ChildWorkflowDetailedSerializer(serializers.ModelSerializer):
    """
    Detailed level serializer for Workflow objects, but with detail instead of self-detail
    """

    author = WorkflowAuthorSummarySerializer()
    workflowstep_set = WorkflowStepSerializer(many=True)
    detail = serializers.HyperlinkedIdentityField(
        view_name="workflow", lookup_field="id"
    )
    images = serializers.SerializerMethodField()
    metadata = serializers.SerializerMethodField()

    class Meta:
        model = Workflow
        fields = (
            "id",
            "detail",
            "code",
            "name",
            "author",
            "images",
            "workflowstep_set",
            "metadata",
        )

    def get_images(self, instance):
        """
        Method to build an object for each corresponding Image.

        Parameters:
            instance (Workflow object)

        Returns:
            List of Image objects in JSON format.

        """
        return get_images_helper(
            self.context.get("request"), instance.workflowimage_set.all()
        )

    def get_metadata(self, instance):
        """
        Helper method for gathering collection metadata

        Parameters:
        instance : WorkflowCollection object

        Returns:
            List of Lists of Metadata associated with the Collection
        """
        metadata_list = []
        for hierarchy in instance.metadata.all():
            metadata_list.append(hierarchy.group_hierarchy)

        return metadata_list

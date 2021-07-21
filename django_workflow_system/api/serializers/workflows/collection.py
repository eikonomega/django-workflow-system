from rest_framework import serializers
from rest_framework.reverse import reverse

from .author import WorkflowAuthorSummarySerializer
from .workflow import WorkflowTerseSerializer, ChildWorkflowDetailedSerializer
from ..utils import get_images_helper
from ....models import (
    WorkflowCollectionMember,
    WorkflowCollection,
    WorkflowCollectionEngagement,
)


class WorkflowCollectionMemberSummarySerializer(serializers.ModelSerializer):
    """
    Summary level serializer for WorkflowCollectionMember objects.
    """

    workflow = WorkflowTerseSerializer()

    class Meta:
        model = WorkflowCollectionMember
        fields = (
            "order",
            "workflow",
        )


class WorkflowCollectionMemberDetailedSerializer(serializers.ModelSerializer):
    """
    Summary level serializer for WorkflowCollectionMember objects, but with steps.
    """

    workflow = ChildWorkflowDetailedSerializer()

    class Meta:
        model = WorkflowCollectionMember
        fields = (
            "order",
            "workflow",
        )


class WorkflowCollectionBaseSerializer(serializers.ModelSerializer):
    """Summary level serializer for WorkflowCollection objects."""

    authors = serializers.SerializerMethodField()
    metadata = serializers.SerializerMethodField()
    newer_version = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    dependencies_completed = serializers.SerializerMethodField()

    def get_authors(self, instance):
        """

        Method to get data for the 'authors' field.
        Returns a list of the Authors for all Workflows linked to a
        WorkflowCollection in JSON format.

        Parameters:
            instance (WorkflowCollection object)

        Returns:
            List of Author objects in JSON format.
        """
        return get_authors_helper(self.context["request"], instance)

    def get_images(self, instance):
        """
        Method to build an object for each corresponding Image.

        Parameters:
            instance (WorkflowCollection object)

        Returns:
            List of Image objects in JSON format.

        """
        return get_images_helper(
            self.context.get("request"), instance.workflowcollectionimage_set.all()
        )

    def get_metadata(self, instance):
        """
        Method to build metadata hierarchy.
        """
        return get_metadata_helper(instance)

    def get_newer_version(self, obj: WorkflowCollection):
        latest_version = (
            WorkflowCollection.objects.filter(code=obj.code, active=True)
            .order_by("version")
            .last()
        )
        if latest_version == None:
            return None
        if obj != latest_version:
            relative_url = reverse(
                "workflow-collection", kwargs={"id": latest_version.id}
            )
            return self.context["request"].build_absolute_uri(relative_url)
        else:
            return None

    def get_dependencies_completed(self, instance):
        """Determine if collection dependencies are fullfilled."""
        request = self.context.get("request")
        status = False

        # If there are no dependencies, we just say they are completed.
        if not instance.collection_dependencies.all():
            status = True

        else:
            # Determine if there is at least one complete engagement
            # for each of the dependencies.
            dependency_engagement_records = [
                WorkflowCollectionEngagement.objects.filter(
                    user=request.user,
                    workflow_collection=dependency,
                    finished__isnull=False,
                )
                for dependency in instance.collection_dependencies.all()
            ]

            status = all(dependency_engagement_records)

        return status


class WorkflowCollectionSummarySerializer(WorkflowCollectionBaseSerializer):
    """
    Summary level serializer for WorkflowCollection objects.
    """

    detail = serializers.HyperlinkedIdentityField(
        view_name="workflow-collection", lookup_field="id"
    )

    class Meta:
        model = WorkflowCollection
        fields = (
            "id",
            "detail",
            "code",
            "version",
            "active",
            "created_date",
            "modified_date",
            "description",
            "assignment_only",
            "recommendable",
            "name",
            "ordered",
            "authors",
            "images",
            "category",
            "metadata",
            "newer_version",
            "dependencies_completed",
        )


class WorkflowCollectionDetailedSerializer(WorkflowCollectionBaseSerializer):
    """
    Detailed level serializer for WorkflowCollection objects.
    """

    workflowcollectionmember_set = WorkflowCollectionMemberSummarySerializer(many=True)
    self_detail = serializers.HyperlinkedIdentityField(
        view_name="workflow-collection", lookup_field="id"
    )

    class Meta:
        model = WorkflowCollection
        fields = (
            "self_detail",
            "id",
            "code",
            "version",
            "active",
            "created_date",
            "modified_date",
            "description",
            "assignment_only",
            "recommendable",
            "name",
            "ordered",
            "workflowcollectionmember_set",
            "authors",
            "images",
            "category",
            "metadata",
            "newer_version",
            "dependencies_completed",
        )


class WorkflowCollectionWithStepsSerializer(WorkflowCollectionBaseSerializer):
    """
    Detailed level serializer for WorkflowCollection objects, but with steps.
    """

    workflowcollectionmember_set = WorkflowCollectionMemberDetailedSerializer(many=True)
    self_detail = serializers.HyperlinkedIdentityField(
        view_name="workflow-collection", lookup_field="id"
    )

    class Meta:
        model = WorkflowCollection
        fields = (
            "self_detail",
            "id",
            "code",
            "version",
            "active",
            "created_date",
            "modified_date",
            "description",
            "assignment_only",
            "recommendable",
            "name",
            "ordered",
            "workflowcollectionmember_set",
            "authors",
            "images",
            "category",
            "metadata",
            "newer_version",
        )


def get_authors_helper(request, instance):
    """
    Helper method for gathering a list of the Authors for all Workflows
    linked to a WorkflowCollection in JSON format.

    Parameters:
        request : self.context['request']
        instance : WorkflowCollection object

    Returns:
        List of Author objects in JSON format.
    """
    authors = []
    for member in instance.workflowcollectionmember_set.all():
        authors.append(
            WorkflowAuthorSummarySerializer(
                member.workflow.author, context={"request": request}
            ).data
        )
    # Ensure that the id's for all authors are unique to avoid duplicate
    # entries
    # Here we're making a dict with the key being the id. This filters out the duplicates.
    # The values() of the dict will be make up the list
    return list({author["id"]: author for author in authors}.values())


def get_metadata_helper(instance):
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

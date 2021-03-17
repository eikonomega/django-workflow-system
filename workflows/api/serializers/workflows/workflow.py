from rest_framework import serializers

from .author import WorkflowAuthorSummarySerializer
from .step import WorkflowStepSummarySerializer
from ....models import Workflow, WorkflowImage


class WorkflowTerseSerializer(serializers.ModelSerializer):
    """
    Terse level serializer for Workflow objects.
    """

    detail = serializers.HyperlinkedIdentityField(
        view_name='workflow-v3', lookup_field='id')

    class Meta:
        model = Workflow
        fields = (
            'name',
            'detail'
        )


class WorkflowSummarySerializer(serializers.ModelSerializer):
    """
    Summary level serializer for Workflow objects.
    """

    detail = serializers.HyperlinkedIdentityField(
        view_name='workflow-v3', lookup_field='id')

    author = WorkflowAuthorSummarySerializer()
    images = serializers.SerializerMethodField()

    class Meta:
        model = Workflow
        fields = (
            'id', 'name', 'detail', 'images', 'author')

    def get_images(self, instance):
        """
        Method to build an object for each corresponding Image.

        Parameters:
            instance (Workflow object)

        Returns:
            List of Image objects in JSON format.

        """
        return get_images_helper(instance)


class WorkflowDetailedSerializer(serializers.ModelSerializer):
    """
    Detailed level serializer for Workflow objects.
    """

    author = WorkflowAuthorSummarySerializer()
    workflowstep_set = WorkflowStepSummarySerializer(many=True)
    self_detail = serializers.HyperlinkedIdentityField(
        view_name='workflow-v3',
        lookup_field='id')
    images = serializers.SerializerMethodField()


    class Meta:
        model = Workflow
        fields = (
            'id', 'self_detail', 'code', 'name', 'author', 'images', 'workflowstep_set')

    def get_images(self, instance):
        """
        Method to build an object for each corresponding Image.

        Parameters:
            instance (Workflow object)

        Returns:
            List of Image objects in JSON format.

        """
        return get_images_helper(instance)


class ChildWorkflowDetailedSerializer(serializers.ModelSerializer):
    """
    Detailed level serializer for Workflow objects, but with detail instead of self-detail
    """

    author = WorkflowAuthorSummarySerializer()
    workflowstep_set = WorkflowStepSummarySerializer(many=True)
    detail = serializers.HyperlinkedIdentityField(
        view_name='workflow-v3',
        lookup_field='id')
    images = serializers.SerializerMethodField()

    class Meta:
        model = Workflow
        fields = (
            'id', 'detail', 'code', 'name', 'author', 'images', 'workflowstep_set')

    def get_images(self, instance):
        """
        Method to build an object for each corresponding Image.

        Parameters:
            instance (Workflow object)

        Returns:
            List of Image objects in JSON format.

        """
        return get_images_helper(instance)


def get_images_helper(instance):
    """
    Helper method for gathering a workflow's list of images and formatting them along with their
    corresponding types.

    Parameters:
    instance : Workflow object

    Returns:
        List of Image objects in JSON format.

    """
    images = []

    for image in instance.workflowimage_set.all():
        image_dict = {
            "image_url": image.image.__str__(),  # TODO: Make this a hyperlink field
            "image_type": image.type.type
        }
        images.append(image_dict)

    return images

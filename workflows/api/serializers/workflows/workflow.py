from rest_framework import serializers

from .author import WorkflowAuthorSummarySerializer
from .step import WorkflowStepSummarySerializer
from ....models import Workflow


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
            'detail',
            'image'
        )


class WorkflowSummarySerializer(serializers.ModelSerializer):
    """
    Summary level serializer for Workflow objects.
    """

    detail = serializers.HyperlinkedIdentityField(
        view_name='workflow-v3', lookup_field='id')

    author = WorkflowAuthorSummarySerializer()

    class Meta:
        model = Workflow
        fields = (
            'id', 'name', 'detail', 'author', 'image')


class WorkflowDetailedSerializer(serializers.ModelSerializer):
    """
    Detailed level serializer for Workflow objects.
    """

    author = WorkflowAuthorSummarySerializer()
    workflowstep_set = WorkflowStepSummarySerializer(many=True)
    self_detail = serializers.HyperlinkedIdentityField(
        view_name='workflow-v3',
        lookup_field='id')

    class Meta:
        model = Workflow
        fields = (
            'id', 'self_detail', 'code', 'name', 'image', 'author', 'workflowstep_set')


class ChildWorkflowDetailedSerializer(serializers.ModelSerializer):
    """
    Detailed level serializer for Workflow objects, but with detail instead of self-detail
    """

    author = WorkflowAuthorSummarySerializer()
    workflowstep_set = WorkflowStepSummarySerializer(many=True)
    detail = serializers.HyperlinkedIdentityField(
        view_name='workflow-v3',
        lookup_field='id')

    class Meta:
        model = Workflow
        fields = (
            'id', 'detail', 'code', 'name', 'image', 'author', 'workflowstep_set')

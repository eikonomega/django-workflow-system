from rest_framework import serializers

from ....models import (
    WorkflowStep,
    WorkflowStepAudio,
    WorkflowStepImage,
    WorkflowStepText,
    WorkflowStepInput,
    WorkflowStepVideo)


class WorkflowStepTextSummarySerializer(serializers.ModelSerializer):
    """
    Summary level serializer for WorkflowStepText objects.
    """
    class Meta:
        model = WorkflowStepText
        fields = (
            'id',
            'workflow_step',
            'content',
            'ui_identifier',
            'storage_value')

class WorkflowStepInputSummarySerializer(serializers.ModelSerializer):
    """
    Summary level serializer for WorkflowStepInput objects.
    """
    class Meta:
        model = WorkflowStepInput
        fields = (
            'id',
            'workflow_step',
            'content',
            'ui_identifier',
            'required',
            'response_schema')


class WorkflowStepAudioSummarySerializer(serializers.ModelSerializer):
    """
    Summary level serializer for WorkflowStepAudio  objects.
    """
    class Meta:
        model = WorkflowStepAudio
        fields = (
            'id',
            'workflow_step',
            'ui_identifier',
            'url')


class WorkflowStepImageSummarySerializer(serializers.ModelSerializer):
    """
    Summary level serializer for WorkflowStepImage objects.
    """
    class Meta:
        model = WorkflowStepImage
        fields = (
            'id',
            'workflow_step',
            'ui_identifier',
            'url')


class WorkflowStepVideoSummarySerializer(serializers.ModelSerializer):
    """
    Summary level serializer for WorkflowStepVideo objects.
    """
    class Meta:
        model = WorkflowStepVideo
        fields = (
            'id',
            'workflow_step',
            'ui_identifier',
            'url')


class WorkflowStepSummarySerializer(serializers.ModelSerializer):
    """
    Summary level serializer for WorkflowStep objects.
    """

    ui_template = serializers.SlugRelatedField(
        slug_field='name', read_only=True)
    workflowstepinput_set = WorkflowStepInputSummarySerializer(many=True)
    workflowsteptext_set = WorkflowStepTextSummarySerializer(many=True)
    workflowstepaudio_set = WorkflowStepAudioSummarySerializer(many=True)
    workflowstepimage_set = WorkflowStepImageSummarySerializer(many=True)
    workflowstepvideo_set = WorkflowStepVideoSummarySerializer(many=True)

    class Meta:
        model = WorkflowStep
        fields = (
            'id', 'code', 'order', 'ui_template',
            'workflowstepinput_set',
            'workflowsteptext_set',
            'workflowstepaudio_set',
            'workflowstepimage_set',
            'workflowstepvideo_set')

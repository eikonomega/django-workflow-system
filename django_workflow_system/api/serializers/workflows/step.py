from rest_framework import serializers

from ....models import (
    WorkflowStep,
    WorkflowStepAudio,
    WorkflowStepImage,
    WorkflowStepText,
    WorkflowStepUserInput,
    WorkflowStepVideo,
    WorkflowStepExternalLink,
)


class WorkflowStepTextSerializer(serializers.ModelSerializer):
    """
    Summary level serializer for WorkflowStepText objects.
    """

    class Meta:
        model = WorkflowStepText
        fields = ("id", "workflow_step", "text", "ui_identifier")


class WorkflowStepExternalLinkSerializer(serializers.ModelSerializer):
    """
    Summary level serializer for WorkflowStepExternalLink objects.
    """

    class Meta:
        model = WorkflowStepExternalLink
        fields = ("id", "workflow_step", "link", "ui_identifier")


class WorkflowStepUserInputSerializer(serializers.ModelSerializer):
    """Summary level serializer for WorkflowStepUserInput objects."""

    type = serializers.SlugRelatedField(slug_field="name", read_only=True)

    class Meta:
        model = WorkflowStepUserInput
        fields = (
            "id",
            "workflow_step",
            "ui_identifier",
            "required",
            "type",
            "specification",
        )


class WorkflowStepAudioSerializer(serializers.ModelSerializer):
    """
    Summary level serializer for WorkflowStepAudio  objects.
    """

    class Meta:
        model = WorkflowStepAudio
        fields = ("id", "workflow_step", "ui_identifier", "url")


class WorkflowStepImageSerializer(serializers.ModelSerializer):
    """
    Summary level serializer for WorkflowStepImage objects.
    """

    class Meta:
        model = WorkflowStepImage
        fields = ("id", "workflow_step", "ui_identifier", "url")


class WorkflowStepVideoSerializer(serializers.ModelSerializer):
    """
    Summary level serializer for WorkflowStepVideo objects.
    """

    class Meta:
        model = WorkflowStepVideo
        fields = ("id", "workflow_step", "ui_identifier", "url")


class WorkflowStepSerializer(serializers.ModelSerializer):
    """
    Summary level serializer for WorkflowStep objects.
    """

    ui_template = serializers.SlugRelatedField(slug_field="name", read_only=True)
    workflowstepuserinput_set = WorkflowStepUserInputSerializer(many=True)
    workflowsteptext_set = WorkflowStepTextSerializer(many=True)
    workflowstepaudio_set = WorkflowStepAudioSerializer(many=True)
    workflowstepimage_set = WorkflowStepImageSerializer(many=True)
    workflowstepvideo_set = WorkflowStepVideoSerializer(many=True)
    workflowstepexternallink_set = WorkflowStepExternalLinkSerializer(many=True)

    class Meta:
        model = WorkflowStep
        fields = (
            "id",
            "code",
            "order",
            "ui_template",
            "workflowstepuserinput_set",
            "workflowsteptext_set",
            "workflowstepaudio_set",
            "workflowstepimage_set",
            "workflowstepvideo_set",
            "workflowstepexternallink_set",
        )

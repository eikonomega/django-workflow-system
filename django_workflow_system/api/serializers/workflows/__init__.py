"""
In the Django Rest Framework, serializers are responsible for converting
native Python objects to HTTP friendly formats (JSON, etc) and vice versa.

You can customize them to mold the output of resource representations.
"""

from .author import WorkflowAuthorSummarySerializer, WorkflowAuthorDetailedSerializer
from .step import (
    WorkflowStepAudioSummarySerializer,
    WorkflowStepSummarySerializer,
    WorkflowStepImageSummarySerializer,
    WorkflowStepTextSummarySerializer,
    WorkflowStepVideoSummarySerializer,
)
from .workflow import WorkflowSummarySerializer, WorkflowDetailedSerializer

__all__ = [
    "WorkflowAuthorSummarySerializer",
    "WorkflowAuthorDetailedSerializer",
    "WorkflowSummarySerializer",
    "WorkflowDetailedSerializer",
    "WorkflowStepSummarySerializer",
    "WorkflowStepAudioSummarySerializer",
    "WorkflowStepImageSummarySerializer",
    "WorkflowStepTextSummarySerializer",
    "WorkflowStepVideoSummarySerializer",
]

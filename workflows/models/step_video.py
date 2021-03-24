"""Django model definition."""
import uuid

from django.db import models

from workflows.models.abstract_models import CreatedModifiedAbstractModel
from workflows.models.step import WorkflowStep


class WorkflowStepVideo(CreatedModifiedAbstractModel):
    """
    Video objects assigned to a WorkflowStep.

    A WorkFlow author is allowed to specify an arbitrary number
    of video elements to a given WorkflowStep.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow_step = models.ForeignKey(
        WorkflowStep,
        on_delete=models.PROTECT,
        help_text="The Workflow Step associated with the video"
    )
    ui_identifier = models.CharField(
        max_length=200,
        help_text="A simple string which is used to indicate to a user "
                  "interface where to display this object within a template"
    )
    url = models.URLField(help_text="The video location")

    class Meta:
        db_table = 'workflow_system_step_video'
        verbose_name_plural = "Workflow Step Videos"
        unique_together = ['workflow_step', 'ui_identifier']

    def __str__(self):
        return self.ui_identifier

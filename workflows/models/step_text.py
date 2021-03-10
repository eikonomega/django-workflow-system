"""Django model definition."""
import uuid

from django.db import models

from workflows.models.abstract_models import CreatedModifiedAbstractModel
from workflows.models.step import WorkflowStep


class WorkflowStepText(CreatedModifiedAbstractModel):
    """
    Text objects assigned to a WorkflowStep.

    A WorkFlow author is allowed to specify an arbitrary number
    of text elements to a given WorkflowStep.

    Attributes:
        id (UUIDField): The unique UUID for the database record.
        workflow_step (ForeignKey): The WorkflowStep object that will own this object.
        ui_identifier (CharField): A simple string which is used to indicate to a user interface
                                   where to display this object within a template.
        content (CharField): The actual text.
        storage_value (IntegerField): The value that will be stored, in place of direct user input.
                                      This is used when multiple WorkflowStepInputs are used to
                                      represent single-choice options.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow_step = models.ForeignKey(
        WorkflowStep,
        on_delete=models.CASCADE)
    ui_identifier = models.CharField(max_length=200)
    content = models.CharField(max_length=500)
    storage_value = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'workflow_system_step_text'
        unique_together = ["workflow_step", "ui_identifier"]
        verbose_name_plural = 'Workflow Step Texts'

    def __str__(self):
        return self.ui_identifier
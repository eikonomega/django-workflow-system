"""Django model definition."""
import uuid

from django.db import models

from workflows.models import JSONSchema
from workflows.models.abstract_models import CreatedModifiedAbstractModel
from workflows.models.step import WorkflowStep


class WorkflowStepInput(CreatedModifiedAbstractModel):
    """
    Question objects assigned to a WorkflowStep.

    A WorkFlow author is allowed to specify an arbitrary number
    of question elements to a given WorkflowStep.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow_step = models.ForeignKey(
        WorkflowStep,
        on_delete=models.CASCADE,
        help_text="The WorkflowStep object that will own this object"
    )
    ui_identifier = models.CharField(
        max_length=200,
        help_text="A simple string which is used to indicate to a "
                  "user interface where to display this object within a template"
    )
    content = models.CharField(max_length=500, help_text="The actual text of the question")
    required = models.BooleanField(
        help_text="True if a value is required for this input in the response JSON"
    )
    response_schema = models.ForeignKey(
        JSONSchema,
        on_delete=models.PROTECT,
        help_text="A JSON Schema specification used to validate/reject user responses"
    )

    class Meta:
        db_table = 'workflow_system_step_input'
        unique_together = ["workflow_step", "ui_identifier"]
        verbose_name_plural = 'Workflow Step Inputs'

    def __str__(self):
        return self.ui_identifier

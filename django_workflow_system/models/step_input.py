"""Django model definition."""
import uuid

from django.db import models

from django_workflow_system.models import JSONSchema
from django_workflow_system.models.abstract_models import CreatedModifiedAbstractModel
from django_workflow_system.models.step import WorkflowStep


class WorkflowStepInput(CreatedModifiedAbstractModel):
    """
    Question objects assigned to a WorkflowStep.

    A WorkFlow author is allowed to specify an arbitrary number
    of question elements to a given WorkflowStep.

    Attributes:
        id (UUIDField): The unique UUID for the database record.
        workflow_step (ForeignKey): The WorkflowStep object that will own this object.
        ui_identifier (CharField): A simple string which is used to indicate
                                   to a user interface where to display this object
                                   within a template.
        content (CharField): The actual text of the question.
        required (BooleanField): True if a value is required for this input in the response JSON
        response_schema (ForeignKey): A JSON Schema specification used to validate/reject user
                                      responses.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow_step = models.ForeignKey(WorkflowStep, on_delete=models.CASCADE)
    ui_identifier = models.CharField(max_length=200)
    content = models.CharField(max_length=500)
    required = models.BooleanField()
    response_schema = models.ForeignKey(JSONSchema, on_delete=models.PROTECT)

    class Meta:
        db_table = "workflow_system_step_input"
        unique_together = ["workflow_step", "ui_identifier"]
        verbose_name_plural = "Workflow Step Inputs"

    def __str__(self):
        return self.ui_identifier

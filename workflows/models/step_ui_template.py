"""Django model definition."""
import uuid

from django.db import models

from workflows.models.abstract_models import CreatedModifiedAbstractModel


class WorkflowStepUITemplate(CreatedModifiedAbstractModel):
    """
    User interface template specification for Workflows.

    While the back-end of the application doesn't care
    about the design of the user interface, it does need to
    indicate to various potential interfaces which design template a
    Workflow author intended to be used for a given Workflow step.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(
        max_length=200,
        unique=True,
        help_text="The name of the step template"
    )

    class Meta:
        db_table = 'workflow_system_step_ui_template'
        verbose_name_plural = 'Workflow UI Templates'

    def __str__(self):
        return self.name

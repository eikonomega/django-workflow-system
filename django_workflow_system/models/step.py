"""Django model definition."""
import uuid

from django.core.validators import MinValueValidator
from django.db import models

from django_workflow_system.models.step_ui_template import WorkflowStepUITemplate
from django_workflow_system.models.abstract_models import CreatedModifiedAbstractModel
from django_workflow_system.models.metadata import WorkflowMetadata
from django_workflow_system.models.workflow import Workflow
from django_workflow_system.utils.validators import validate_code


class WorkflowStep(CreatedModifiedAbstractModel):
    """
    Every workflow is comprised of one or more "steps".

    - Each Step MAY have one or more associated StepText objects.
    - Each Step MAY have one or more associated StepVideo objects.
    - Each Step MAY have one or more associated StepImage objects.
    - Each Step MAY have one or more associated StepAudio objects.
    - Each Step MAY have one or more associated StepInput objects.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow = models.ForeignKey(
        Workflow,
        on_delete=models.CASCADE,
        help_text="The workflow associated with the step.",
    )
    code = models.CharField(
        max_length=200,
        help_text="An identifier for programmatically referencing this step.",
        validators=[validate_code],
    )
    order = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text="The order in which this step occurs in the workflow.",
    )
    ui_template = models.ForeignKey(
        WorkflowStepUITemplate,
        on_delete=models.PROTECT,
        help_text="The UI template associated with the step.",
    )
    metadata = models.ManyToManyField(
        WorkflowMetadata,
        blank=True,
        help_text="A list of data groups that this step is associated with.",
    )

    class Meta:
        db_table = "workflow_system_step"
        unique_together = [["workflow", "code"], ["workflow", "order"]]
        verbose_name_plural = "Workflow Steps"
        ordering = ["-workflow", "order"]

    def __str__(self):
        return "{} - {}".format(self.workflow.name, self.code)

import uuid

from django.core.validators import MinValueValidator
from django.db import models

from workflows.models.step_ui_template import WorkflowStepUITemplate
from workflows.models.abstract_models import CreatedModifiedAbstractModel
from workflows.models.data_group import WorkflowStepDataGroup
from workflows.models.workflow import Workflow


class WorkflowStep(CreatedModifiedAbstractModel):
    """
    Every workflow is comprised of one or more "steps" that a user
    must complete in order to finish it.

    - Each Step MAY have one or more associated StepText objects.
    - Each Step MAY have one or more associated StepVideo objects.
    - Each Step MAY have one or more associated StepImage objects.
    - Each Step MAY have one or more associated StepAudio objects.
    - Each Step MAY have one or more associated StepInput objects.

    Attributes:
        id (UUIDField): The UUID for the database record.
        workflow (ForeignKey): The Workflow associated with the step
        code (CharField): The identifying code of the step
        order (PositiveIntegerField): The order in which the step occurs
        ui_template (ForeignKey): The ui template associated with the step
        data_groups (ManyToMany): A list of workflow step data groups this step belongs to

    Notes:
        There is some unusual syntax on "unique" constraints for this model that
        developers may not be used to seeing. Essentially, we specify
        that there are two separate uniqueness contraints to fulfill:
            * workflow/code combination must be unique
            * workflow/order combination must be unique
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE)
    code = models.CharField(max_length=200)
    order = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    ui_template = models.ForeignKey(
        WorkflowStepUITemplate,
        on_delete=models.PROTECT)
    data_groups = models.ManyToManyField(WorkflowStepDataGroup, blank=True)

    class Meta:
        db_table = 'workflow_system_step'
        unique_together = [["workflow", "code"], ["workflow", "order"]]
        verbose_name_plural = 'Workflow Steps'
        ordering = ['-workflow', 'order']

    def __str__(self):
        return "{} - {}".format(
            self.workflow.name,
            self.code)

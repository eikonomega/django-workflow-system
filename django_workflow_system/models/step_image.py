"""Django model definition."""
import uuid

from django.db import models

from django_workflow_system.models.abstract_models import CreatedModifiedAbstractModel
from django_workflow_system.models.step import WorkflowStep

from django_workflow_system.utils import workflow_step_media_location


class WorkflowStepImage(CreatedModifiedAbstractModel):
    """
    Image objects assigned to a WorkflowStep.

    A WorkFlow author is allowed to specify an arbitrary number
    of images elements to a given WorkflowStep.

    Attributes:
        id (UUIDField): The unique UUID for the database record.
        workflow_step (ForeignKey): The Workflow Step associated with the Image
        ui_identifier (CharField): A simple string which is used to indicate
                                   to a user interface where to display this object
                                   within a template.
        url (ImageField): The image location
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow_step = models.ForeignKey(WorkflowStep, on_delete=models.PROTECT)
    ui_identifier = models.CharField(max_length=200)
    url = models.ImageField(upload_to=workflow_step_media_location, max_length=200)

    class Meta:
        db_table = "workflow_system_step_image"
        verbose_name_plural = "Workflow Step Images"
        unique_together = ["workflow_step", "ui_identifier"]

    def __str__(self):
        return self.ui_identifier

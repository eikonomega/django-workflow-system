"""Django model definition."""
import uuid

from django.db import models

from django_workflow_system.models.workflow import Workflow
from django_workflow_system.models.abstract_models import CreatedModifiedAbstractModel
from django_workflow_system.models.workflow_image_type import WorkflowImageType
from django_workflow_system.utils import workflow_image_location


class WorkflowImage(CreatedModifiedAbstractModel):
    """Image for a Workflow."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow = models.ForeignKey(Workflow, on_delete=models.PROTECT)
    type = models.ForeignKey(WorkflowImageType, on_delete=models.PROTECT)
    image = models.ImageField(upload_to=workflow_image_location, max_length=200)

    class Meta:
        db_table = "workflow_system_workflow_image"
        verbose_name_plural = "Workflow Images"
        unique_together = [["workflow", "type"]]

    def __str__(self):
        return self.image.__str__()

    def unique_error_message(self, model_class, unique_check):
        if model_class == type(self) and unique_check == ("workflow", "type"):
            return (
                f"Workflow already has an image of type '{self.type.type}'. This image "
                f"can be replaced above."
            )
        else:
            return super(WorkflowImage, self).unique_error_message(
                model_class, unique_check
            )

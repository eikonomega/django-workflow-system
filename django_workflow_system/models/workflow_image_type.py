"""Django model definition."""
import uuid

from django.db import models

from django_workflow_system.models.abstract_models import CreatedModifiedAbstractModel


class WorkflowImageType(CreatedModifiedAbstractModel):
    """Types that can be assigned to a workflow image."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type = models.CharField(max_length=50, unique=True)

    class Meta:
        db_table = "workflow_system_workflow_image_type"
        verbose_name_plural = "Workflow Image Types"

    def __str__(self):
        return self.type

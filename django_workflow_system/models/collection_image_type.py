"""Django model definition."""
import uuid

from django.db import models

from django_workflow_system.models.abstract_models import CreatedModifiedAbstractModel


class WorkflowCollectionImageType(CreatedModifiedAbstractModel):
    """Types that can be assigned to a collection image."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type = models.CharField(max_length=50, unique=True)

    class Meta:
        db_table = "workflow_system_collection_image_type"
        verbose_name_plural = "Workflow Collection Image Types"

    def __str__(self):
        return self.type

"""Django model definition."""
import uuid

from django.db import models

from django_workflow_system.models.abstract_models import CreatedModifiedAbstractModel
from django_workflow_system.models.collection import WorkflowCollection
from django_workflow_system.models.collection_tag import WorkflowCollectionTagOption


class WorkflowCollectionTagAssignment(CreatedModifiedAbstractModel):
    """Assign tags to collections."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow_collection = models.ForeignKey(
        WorkflowCollection, on_delete=models.CASCADE
    )
    workflow_collection_tag = models.ForeignKey(
        WorkflowCollectionTagOption, on_delete=models.CASCADE
    )

    class Meta:
        db_table = "workflow_system_collection_tag_assignment"
        verbose_name_plural = "Workflow Collections Tag Assignments"

"""Django model definition."""
import uuid

from django.db import models

from django_workflow_system.models.collection_tag_type import WorkflowCollectionTagType
from django_workflow_system.models.abstract_models import CreatedModifiedAbstractModel


class WorkflowCollectionTagOption(CreatedModifiedAbstractModel):
    """
    This model defines tags that may be associated with collections.

    In simple terms, this table defines the set of available tags
    which are then referred to via foreign keys in WorkflowTag objects.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    text = models.CharField(max_length=50, unique=True)
    type = models.ForeignKey(WorkflowCollectionTagType, on_delete=models.PROTECT)

    class Meta:
        db_table = "workflow_system_collection_tag_option"
        verbose_name_plural = "Workflow Collection Tags"

    def __str__(self):
        return f"{self.type}: {self.text}"

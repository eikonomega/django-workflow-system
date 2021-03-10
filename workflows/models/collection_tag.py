"""Django model definition."""
import uuid

from django.db import models

from workflows.models.abstract_models import CreatedModifiedAbstractModel


class WorkflowCollectionTagOption(CreatedModifiedAbstractModel):
    """
    This model defines tags that may be associated with collections.

    In simple terms, this table defines the set of available tags
    which are then referred to via foreign keys in WorkflowTag objects.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    text = models.CharField(max_length=50, unique=True)
    # TODO: Add foreign key to new WorkflowCollectionTagType model. See Github issue for more detail.

    class Meta:
        db_table = "workflow_system_collection_tag_option"
        verbose_name_plural = "Workflow Collection Tags"

    def __str__(self):
        # TODO: Update this when foreign key is in-place to new model.
        return self.text

"""Django model definition."""
import uuid

from django.db import models

from django_workflow_system.models.collection import WorkflowCollection
from django_workflow_system.models.collection_image_type import (
    WorkflowCollectionImageType,
)
from django_workflow_system.models.abstract_models import CreatedModifiedAbstractModel
from django_workflow_system.utils import collection_image_location


class WorkflowCollectionImage(CreatedModifiedAbstractModel):
    """Image for a Workflow Collection."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    collection = models.ForeignKey(WorkflowCollection, on_delete=models.PROTECT)
    type = models.ForeignKey(WorkflowCollectionImageType, on_delete=models.PROTECT)
    image = models.ImageField(upload_to=collection_image_location, max_length=200)

    class Meta:
        db_table = "workflow_system_collection_image"
        verbose_name_plural = "Workflow Collection Images"
        unique_together = [["collection", "type"]]

    def __str__(self):
        return self.image.__str__()

    def unique_error_message(self, model_class, unique_check):
        if model_class == type(self) and unique_check == ("collection", "type"):
            return (
                f"Collection already has an image of type '{self.type.type}'. This image "
                f"can be replaced above."
            )
        else:
            return super(WorkflowCollectionImage, self).unique_error_message(
                model_class, unique_check
            )

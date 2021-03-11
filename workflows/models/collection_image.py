"""Django model definition."""
import uuid

from django.db import models

from workflows.models.collection import WorkflowCollection
from workflows.models.collection_image_type import WorkflowCollectionImageType
from workflows.models.abstract_models import CreatedModifiedAbstractModel


def collection_library_image_location(instance, filename):
    return "workflows/collections/{}/{}.{}".format(instance.id,
                                                   instance.type,
                                                   filename.rpartition(".")[2])


class WorkflowCollectionImage(CreatedModifiedAbstractModel):
    """Image for a Workflow Collection."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    collection = models.ForeignKey(WorkflowCollection, on_delete=models.PROTECT)
    type = models.ForeignKey(WorkflowCollectionImageType, on_delete=models.PROTECT)
    image = models.ImageField(upload_to=collection_library_image_location, max_length=200)

    class Meta:
        db_table = "workflow_system_collection_image"
        verbose_name_plural = "Workflow Collection Images"

    def __str__(self):
        return self.image.__str__()

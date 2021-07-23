"""Django model definition."""
import uuid

from django.core.validators import MinValueValidator
from django.db import models

from django_workflow_system.models.collection import WorkflowCollection
from django_workflow_system.models.workflow import Workflow
from django_workflow_system.models.abstract_models import CreatedModifiedAbstractModel


class WorkflowCollectionMember(CreatedModifiedAbstractModel):
    """Workflow collections are made up of individual workflows, which are called members."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE)
    workflow_collection = models.ForeignKey(
        WorkflowCollection, on_delete=models.CASCADE
    )
    order = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    class Meta:
        db_table = "workflow_system_collection_member"
        unique_together = [
            ["workflow", "workflow_collection"],
            ["workflow_collection", "order"],
        ]
        verbose_name_plural = "Workflow Collection Members"
        ordering = ["order"]

    def __str__(self):
        return "{} - {}".format(self.workflow.name, self.workflow_collection.name)

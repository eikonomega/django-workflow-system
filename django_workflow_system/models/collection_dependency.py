"""Django model definition."""
import uuid

from django.db import models
from django.core.exceptions import ValidationError

from .abstract_models import CreatedModifiedAbstractModel


class WorkflowCollectionDependency(CreatedModifiedAbstractModel):
    """
    Used to indicate when a user must complete one collection before
    being able to create engagements for another collection.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    source = models.ForeignKey(
        "WorkflowCollection",
        on_delete=models.PROTECT,
        related_name="source_workflow_collection",
        help_text="The collection for which we want to create a dependency.",
    )
    target = models.ForeignKey(
        "WorkflowCollection",
        on_delete=models.PROTECT,
        related_name="target_workflow_collection",
        help_text="The collection which we want to require be completed before the user can create engagements for the 'source' collection.",
    )

    class Meta:
        db_table = "workflow_system_collection_dependency"
        verbose_name_plural = "Workflow Collection Dependencies"
        unique_together = [["source", "target"]]

    def save(self, *args, **kwargs):
        self.full_clean()
        super(WorkflowCollectionDependency, self).save(*args, **kwargs)

    def clean(self, *args, **kwargs):
        """Perform a couple of data sanity checks."""
        if WorkflowCollectionDependency.objects.filter(
            source=self.target, target=self.source
        ):
            raise ValidationError(
                f"You are attempt to create a circular dependency. There is already a dependency from {self.target} to {self.source}."
            )

        if self.source == self.target:
            raise ValidationError(
                "You can't create a dependency to the same collection."
            )

    def __str__(self):
        return f"{self.source} requires that all workflows in {self.target} have been completed."

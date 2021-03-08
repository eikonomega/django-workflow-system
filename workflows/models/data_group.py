"""Django model definition."""
import uuid

from django.db import models

from workflows.models.abstract_models import CreatedModifiedAbstractModel


class WorkflowStepDataGroup(CreatedModifiedAbstractModel):
    """
    Definition of a WorkflowStepDataGroup

    Attributes:
        id (UUIDField): The UUID of the DataGroup
        parent_group (ForeignKey): The parent group of this folder. 'blank' signifies this DataGroup has no parent
        name (CharField): Human friendly name.
        description (TextField): The description of the data group.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    parent_group = models.ForeignKey(
        "self",
        default=None,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=200)
    description = models.TextField()

    class Meta:
        db_table = "workflow_system_data_group"
        verbose_name_plural = "Workflow Step Data Groups"

    def __str__(self):
        return self.full_path

    @property
    def full_path(self):
        return "<".join(reversed(self.name_list))

    @property
    def name_list(self):
        """Returns a list of category codes from root to this category"""
        label_list = [self.name]
        iter_group: WorkflowStepDataGroup = self.parent_group
        while iter_group is not None:
            label_list.append(iter_group.name)
            iter_group = iter_group.parent_group
        return tuple(reversed(label_list))

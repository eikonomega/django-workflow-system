"""Django model definition."""
import uuid

from django.db import models

from workflows.models.abstract_models import CreatedModifiedAbstractModel


class WorkflowStepDataGroup(CreatedModifiedAbstractModel):
    """
    WorkflowStepDataGroup allows clients to group together user-provided data.

    This is especially useful for clients who are conducting surveys as
    it allows them to group together data from steps that work together
    to form a single metric.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    parent_group = models.ForeignKey(
        "self",
        default=None,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        help_text="Data groups can be arranged in hierarchies.",
    )
    name = models.CharField(max_length=200)
    description = models.TextField(help_text="The description of the data group.")

    class Meta:
        db_table = "workflow_system_data_group"
        verbose_name_plural = "Workflow Step Data Groups"

    def __str__(self):
        return self.full_path

    @property
    def full_path(self):
        # TODO: Add description.
        return "<".join(reversed(self.name_list))

    @property
    def name_list(self):
        # TODO: Rename to something like "group_hierarchy" and improve documentation.
        """Return a list of category codes from root to this category"""
        label_list = [self.name]
        iter_group: WorkflowStepDataGroup = self.parent_group
        while iter_group is not None:
            label_list.append(iter_group.name)
            iter_group = iter_group.parent_group
        return tuple(reversed(label_list))

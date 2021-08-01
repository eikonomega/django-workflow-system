"""Django model definition."""
import uuid

from django.core.exceptions import ValidationError
from django.db import models

from django_workflow_system.models.abstract_models import CreatedModifiedAbstractModel


class WorkflowMetadata(CreatedModifiedAbstractModel):
    """
    WorkflowMetadata allows clients to group together user-provided data.

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
        db_table = "workflow_system_metadata"
        verbose_name_plural = "Workflow Metadata"
        unique_together = ["name", "parent_group"]

    def __str__(self):
        return self.full_path

    @property
    def full_path(self):
        """
        This will return the hierarchy of this data group in a string format.
        """
        return " -> ".join(self.group_hierarchy)

    @property
    def group_hierarchy(self):
        """
        Return a list of category codes in their hierarchical form. This will start at
        this group and traverse upwards grabbing all parents until we reach the root group.

        We then reverse this list so it is returned in the proper hierarchical form.
        """
        label_list = [self.name]
        iter_group: WorkflowMetadata = self.parent_group
        while iter_group is not None:
            label_list.append(iter_group.name)
            iter_group = iter_group.parent_group
        return tuple(reversed(label_list))

    def clean(self, *args, **kwargs):
        """
        Ensure that the metadata name doesn't already exist at this level.
        """
        # Get all metadata objects
        for obj in WorkflowMetadata.objects.all():
            if (
                obj.name.lower() == self.name.lower()
                and obj.parent_group == self.parent_group
            ):
                raise ValidationError(
                    {
                        "name": f"Name '{self.name}' with this same parent group already exists."
                    }
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super(WorkflowMetadata, self).save(*args, **kwargs)

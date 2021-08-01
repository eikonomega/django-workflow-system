"""Django model definition."""
import uuid

from django.conf import settings
from django.db import models

from django_workflow_system.models.abstract_models import CreatedModifiedAbstractModel
from django_workflow_system.models.author import WorkflowAuthor
from django_workflow_system.models.metadata import WorkflowMetadata
from django_workflow_system.utils.validators import validate_code
from django_workflow_system.utils.version_validator import version_validator


class Workflow(CreatedModifiedAbstractModel):
    """
    This is the primary model for this feature.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="The UUID of the Workflow",
    )
    code = models.CharField(
        max_length=200,
        validators=[validate_code],
        help_text="An internal code for database level operations",
    )
    name = models.CharField(max_length=200, help_text="Human friendly name")
    version = models.PositiveIntegerField(
        default=1,
        help_text="The version of a Workflow. Used to accommodate the "
        "evolution of a Workflow over time",
    )
    author = models.ForeignKey(
        WorkflowAuthor, on_delete=models.PROTECT, help_text="The author of the Workflow"
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        limit_choices_to={"is_staff": True},
        help_text="Administrative user who created the Workflow in the database",
    )
    metadata = models.ManyToManyField(
        WorkflowMetadata,
        blank=True,
        help_text="A list of metadata that this workflow is associated with.",
    )
    on_completion = models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        db_table = "workflow_system_workflow"
        unique_together = ["version", "code"]
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def clean(self):
        version_validator(self, Workflow)

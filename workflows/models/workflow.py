"""Django model definition."""
import uuid

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Max

from workflows.models.abstract_models import CreatedModifiedAbstractModel
from workflows.models.author import WorkflowAuthor
from workflows.utils.validators import validate_code


class Workflow(CreatedModifiedAbstractModel):
    """
    This is the primary model for this feature.
    """

    IMAGE_SIZE = (600, 375)

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="The UUID of the Workflow"
    )
    code = models.CharField(
        max_length=200,
        validators=[validate_code],
        help_text="An internal code for database level operations"
    )
    name = models.CharField(max_length=200, help_text="Human friendly name")
    version = models.PositiveIntegerField(
        default=1,
        help_text="The version of a Workflow. Used to accommodate the "
                  "evolution of a Workflow over time"
    )
    author = models.ForeignKey(
        WorkflowAuthor,
        on_delete=models.PROTECT,
        help_text="The author of the Workflow"
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        limit_choices_to={"is_staff": True},
        help_text="Administrative user who created the Workflow in the database"
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
        previous_workflows = Workflow.objects.filter(code=self.code)
        latest_version = previous_workflows.aggregate(Max('version'))['version__max']

        # If this is a new workflow code then make sure the version is 1.
        if not latest_version and self.version != 1:
            raise ValidationError({"version": f"Version must be 1 for new workflow codes."})

        # If the first and only workflow of a certain code is attempting to be updated with a different code.
        if previous_workflows.count() == 1 and previous_workflows[0].id == self.id and self.version != 1:
            raise ValidationError({"version": f"Version must be 1 for the first workflow of a code."})

        # Validate that this workflow code's version is not incrementing by more than 1
        if latest_version and self.version > latest_version + 1:
            raise ValidationError({"version": f"Version can only be incremented by 1. "
                                              f"The current latest version of this workflow code "
                                              f"is {latest_version}."})

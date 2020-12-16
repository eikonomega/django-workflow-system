import uuid

from django.contrib.auth.models import User
from django.db import models

from workflows.models.abstract_models import CreatedModifiedAbstractModel
from workflows.models.author import WorkflowAuthor


# Utility Functions for Handling Media Uploads
def workflow_cover_image_location(instance, filename):
    return 'workflows/workflows/{}/cover-image.{}'.format(
        instance.id, filename.rpartition('.')[2])


class Workflow(CreatedModifiedAbstractModel):
    """
    This is the primary model for this feature.
    All other models in this application bear
    a direct/indirect relationship to this one.

    Attributes:
        id (UUIDField): The UUID of the Workflow
        code (CharField): An internal code for database level operations.
        name (CharField): Human friendly name.
        version (PositiveIntegerField): The version of a Workflow. Used to accomodate the 
                                        evolution of a Workflow over time.
        image (ImageField): General image associated with the Workflow.
        author (ForeignKey): The author of the Workflow
        created_by (ForeignKey): Administrative user who created the Workflow
                                 in the database.
    """

    IMAGE_SIZE = (600, 375)

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    version = models.PositiveIntegerField(default=1)
    image = models.ImageField(
        upload_to=workflow_cover_image_location,
        max_length=200,
        blank=True,
        null=True,
    )
    author = models.ForeignKey(WorkflowAuthor, on_delete=models.PROTECT)
    created_by = models.ForeignKey(
        User, on_delete=models.PROTECT, limit_choices_to={'is_staff': True})
    on_completion = models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        db_table = 'workflow_system_workflow'
        unique_together = ['version', 'code']
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

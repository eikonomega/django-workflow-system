import uuid

from django.db import models
from django.contrib.auth.models import User

from workflows.models.abstract_models import CreatedModifiedAbstractModel


def workflow_author_media_folder(instance, filename):
    return 'workflows/authors/{}/profileImage.{}'.format(
        instance.id, filename.rpartition('.')[2])


class WorkflowAuthor(CreatedModifiedAbstractModel):
    """
    Author model/table for Workflows

    Assignments
    -----------
    id : uuid
        The unique UUID of the record.
    user : onetoone
        The user associated with the author.
    title : charfield
        The title associated with the author.
    image : imagefield
        The image associated with the author.
    biography : textfield
        Biography of the author.

    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    title = models.CharField(max_length=200)
    image = models.ImageField(
        upload_to=workflow_author_media_folder,
        max_length=200,
        null=True)
    biography = models.TextField(max_length=500)

    class Meta:
        db_table = "workflow_system_author"
        verbose_name_plural = "Workflow Authors"

    def __str__(self):
        return str(self.user)

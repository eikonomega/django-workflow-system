import uuid

from django.contrib.auth.models import User
from django.db import models
from django.core.validators import MinValueValidator

from workflows.models.abstract_models import CreatedModifiedAbstractModel
from workflows.models.workflow import Workflow


# Utility Functions for Handling Media Uploads
def collection_detail_image_location(instance, filename):
    return "workflows/collections/{}/detail-image.{}".format(
        instance.id, filename.rpartition(".")[2]
    )


def collection_home_image_location(instance, filename):
    return "workflows/collections/{}/home-image.{}".format(
        instance.id, filename.rpartition(".")[2]
    )


def collection_library_image_location(instance, filename):
    return "workflows/collections/{}/library-image.{}".format(
        instance.id, filename.rpartition(".")[2]
    )


def collection_cover_image_location(instance, filename):
    return "workflows/collections/{}/cover-image.{}".format(
        instance.id, filename.rpartition(".")[2]
    )


class WorkflowCollectionTagOption(CreatedModifiedAbstractModel):
    """
    This table defines what options are available to use as tags.

    In simple terms, this table defines the set of available tags
    which are then referred to via foreign keys in WorkflowTag objects.

    Attributes:
        id (UUIDField): The unique UUID of the object.
        text (CharField): The unique text of the tag.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    text = models.CharField(max_length=50, unique=True)

    class Meta:
        db_table = "workflow_system_collection_tag_option"
        verbose_name_plural = "Workflow Collection Tags"

    def __str__(self):
        return self.text


class WorkflowCollection(CreatedModifiedAbstractModel):
    """
    Definition of a Workflow collection.

    Conceptually, this model exists to provide the ability
    to group/collect a set of individual Workflows
    into a sort of "meta-Workflow".

    Attributes:
        id (UUIDField): The unique UUID of the record.
        code (CharField): Code associated with the Workflow Collection.
        name (CharField): The name of the Workflow Collection.
        description (TextField): The description of the Workflow Collection.
        ordered (BooleanField): Indicated whether the workflow runs in a certain order.
        detail_image (ImageField): Detail image associated with the collection.
        home_image (ImageField): Home image associated with the collection.
        library_image (ImageField): Library image associated with the collection.
        version (PositiveIntegerField): The version of a Workflow Collection. Used to accommodate
                                        the evolution of a Workflow over time.
        created_by (ForeignKey): Administrative user who created the Workflow in the database.
        assignment_only (BooleanField): If True, the Workflow should only be accessible via assignment.
        active (BooleanField): Indication of whether or not the Workflow Collection is
                               currently available for use.
        category (CharField): The "type" of Workflow.
        tags (ManyToMany): A 'list' of tags associated to the collection
    """

    HOME_IMAGE_SIZE = (975, 600)
    DETAIL_IMAGE_SIZE = (1125, 1050)
    LIBRARY_IMAGE_SIZE = (825, 600)

    WORKFLOW_TYPES = (
        ("SURVEY", "survey"),
        ("ACTIVITY", "activity"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=200, unique=False)
    name = models.CharField(max_length=200, unique=False)
    description = models.TextField()
    ordered = models.BooleanField()
    detail_image = models.ImageField(
        upload_to=collection_detail_image_location, max_length=200
    )
    home_image = models.ImageField(
        upload_to=collection_home_image_location, max_length=200
    )
    library_image = models.ImageField(
        upload_to=collection_library_image_location, max_length=200
    )
    version = models.PositiveIntegerField(default=1)
    created_by = models.ForeignKey(
        User, on_delete=models.PROTECT, limit_choices_to={"is_staff": True}
    )
    assignment_only = models.BooleanField(default=False)
    active = models.BooleanField()
    category = models.CharField(default=None, choices=WORKFLOW_TYPES, max_length=8)

    tags = models.ManyToManyField(
        WorkflowCollectionTagOption,
        through="WorkflowCollectionTag")

    class Meta:
        db_table = "workflow_system_collection"
        verbose_name_plural = "Workflow Collections"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=['code', 'version'],
                name="Code and version combined must be unique"
            ),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def source_identifier(self):
        return f"{self.code}_v{self.version}"


class WorkflowCollectionTag(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow_collection = models.ForeignKey(WorkflowCollection, on_delete=models.CASCADE)
    workflow_collection_tag = models.ForeignKey(
        WorkflowCollectionTagOption, on_delete=models.CASCADE)

    class Meta:
        db_table = "workflow_system_collection_tag"
        verbose_name_plural = "Workflow Collections Tags"


class WorkflowCollectionMember(CreatedModifiedAbstractModel):
    """
    Definition of a Workflow Collection Member.

    Attributes:
        id (UUIDField): The unique UUID of the record.
        workflow (ForeignKey): The workflow attached to the collection member.
        workflow_collection (ForeignKey): The workflow collection attached the the collection member.
        order (PositiveIntegerField): The order of the WorkflowCollection.
    """
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

    def __str__(self):
        return "{} - {}".format(self.workflow.name, self.workflow_collection.name)

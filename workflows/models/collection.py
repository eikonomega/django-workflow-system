"""Django model definition."""
import re
import uuid

from django.contrib.auth.models import User
from django.db import models
from django.core.exceptions import ValidationError

from workflows.models.abstract_models import CreatedModifiedAbstractModel
from workflows.models.collection_tag import WorkflowCollectionTagOption


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


def validate_code(code):
    """
    Ensure that the code provided follows python_variable_naming_syntax.
    """
    regex = '^[a-z_][a-z0-9_]+$'
    if not re.search(regex, code):
        raise ValidationError("code must be in 'python_variable_naming_syntax'")


class WorkflowCollection(CreatedModifiedAbstractModel):
    """
    Definition of a Workflow Collection.

    Workflow collections are the highest level of abstraction in the data model.
    Individual workflows are grouped together via collections.

        created_by (ForeignKey): Administrative user who created the Workflow in the database.
        assignment_only (BooleanField): If True, the Workflow should only be accessible via assignment.
        active (BooleanField): Indication of whether or not the Workflow Collection is
                               currently available for use.
        category (CharField): The "type" of Workflow.
        tags (ManyToMany): A 'list' of tags associated to the collection
    """

    COLLECTION_TYPES = (
        ("SURVEY", "survey"),
        ("ACTIVITY", "activity"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # When taken together the next two fields uniquely identify a given collection.
    # We use code instead of name for this purpose because it has a stricter syntax.
    code = models.CharField(max_length=200, unique=False, validators=[validate_code])
    version = models.PositiveIntegerField(default=1)

    # Human friendly name for the collection.
    name = models.CharField(max_length=200, unique=False)
    description = models.TextField()

    # Do all workflows in collection need to be completed in order?
    ordered = models.BooleanField()

    # TODO: Delete these. See GH issue #12
    detail_image = models.ImageField(
        upload_to=collection_detail_image_location, max_length=200
    )
    home_image = models.ImageField(
        upload_to=collection_home_image_location, max_length=200
    )
    library_image = models.ImageField(
        upload_to=collection_library_image_location, max_length=200
    )

    # Which staff member created the collection in the admin panel?
    # This is separate from Workflow author, and just points to the
    # person to did the administrative work to create the collection.
    created_by = models.ForeignKey(
        User, on_delete=models.PROTECT, limit_choices_to={"is_staff": True}
    )

    # Is collection on available via assignment?
    assignment_only = models.BooleanField(default=False)

    # Indicate if collection is eligible for recommendations.
    recommendable = models.BooleanField()

    # Indicates if collection is ready for use.
    active = models.BooleanField()

    # Collections can either represent a survey or a set of activities.
    # This may expand in the future.
    category = models.CharField(default=None, choices=COLLECTION_TYPES, max_length=8)

    tags = models.ManyToManyField(
        WorkflowCollectionTagOption, through="WorkflowCollectionTagAssignment"
    )

    class Meta:
        db_table = "workflow_system_collection"
        verbose_name_plural = "Workflow Collections"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["code", "version"],
                name="Code and version combined must be unique",
            ),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.full_clean()
        super(WorkflowCollection, self).save(*args, **kwargs)

    def source_identifier(self):
        return f"{self.code}_v{self.version}"


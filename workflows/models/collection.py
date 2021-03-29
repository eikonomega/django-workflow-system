"""Django model definition."""
import uuid

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Max

from workflows.models.abstract_models import CreatedModifiedAbstractModel
from workflows.models.collection_tag import WorkflowCollectionTagOption
from workflows.utils.validators import validate_code


class WorkflowCollection(CreatedModifiedAbstractModel):
    """
    Definition of a Workflow Collection.

    Workflow collections are the highest level of abstraction in the data model.
    Individual workflows are grouped together via collections.

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
    version = models.PositiveIntegerField(
        default=1,
        help_text="""
        Version of the collection. When you change a collection, you should 
        create a new version rather than modify an existing one.
        """
    )

    name = models.CharField(
        max_length=200,
        unique=False,
        help_text="Human friendly name for the collection."
    )
    description = models.TextField()

    ordered = models.BooleanField(
        help_text="Do all workflows in collection need to be completed in order?"
    )

    # Which staff member created the collection in the admin panel?
    # This is separate from Workflow author, and just points to the
    # person to did the administrative work to create the collection.
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        limit_choices_to={"is_staff": True},
        help_text="Administrative user who created the collection in the database."
    )

    assignment_only = models.BooleanField(
        default=False, help_text="Is this collection only available via assignment?"
    )

    # Indicate if collection is eligible for recommendations.
    recommendable = models.BooleanField(
        default=False, help_text="Is this collection available for recommendations?"
    )

    active = models.BooleanField(
        default=False, help_text="Indicates if collection is ready for use."
    )

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

    def clean(self):
        # Validate that this collection code's version is not incrementing by more than 1
        previous_collections = WorkflowCollection.objects.filter(code=self.code)
        latest_version = previous_collections.aggregate(Max('version'))['version__max']

        # If this is a new collection code then make sure the version is 1.
        if not latest_version and self.version != 1:
            raise ValidationError({"version": f"Version must be 1 for new collection codes."})

        # If the first and only collection of a certain code is attempting to be updated with a different code.
        if previous_collections.count() == 1 and previous_collections[0].id == self.id and self.version != 1:
            raise ValidationError({"version": f"Version must be 1 for the first collection of a code."})

        # Validate that this collection code's version is not incrementing by more than 1
        if latest_version and self.version > latest_version + 1:
            raise ValidationError({"version": f"Version can only be incremented by 1. "
                                              f"The current latest version of this collection code "
                                              f"is {latest_version}."})

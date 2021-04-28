"""Django model definition."""
import uuid
from datetime import date

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models import Q

from django_workflow_system.models.abstract_models import CreatedModifiedAbstractModel
from django_workflow_system.models.engagement import WorkflowCollectionEngagement
from django_workflow_system.models.collection import WorkflowCollection


class WorkflowCollectionAssignment(CreatedModifiedAbstractModel):
    """
    Definition of a Workflow Collection Assignment.

    Workflow collections can be assigned to users. A common use-case
    for this is when an application needs to assign a survey collection
    to a user or group of users.
    """

    ASSIGNED = "ASSIGNED"
    IN_PROGRESS = "IN_PROGRESS"
    CLOSED_INCOMPLETE = "CLOSED_INCOMPLETE"
    CLOSED_COMPLETE = "CLOSED_COMPLETE"

    STATUS_CHOICES = (
        (ASSIGNED, "Assigned"),
        (IN_PROGRESS, "In Progress"),
        (CLOSED_INCOMPLETE, "Closed (Incomplete)"),
        (CLOSED_COMPLETE, "Closed (Complete)"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    workflow_collection = models.ForeignKey(
        WorkflowCollection, on_delete=models.CASCADE
    )

    # FK to Django user.
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)

    # TODO: If time allows, we should make these datetime fields to allow users to have more precise control over assignements.
    assigned_on = models.DateField(default=date.today)
    expiration = models.DateField(default=settings.WORKFLOWS_DEFAULT_EXPIRATION)
    status = models.CharField(choices=STATUS_CHOICES, max_length=17, default=ASSIGNED)

    # Used to track if a collection engagement has been associated with this assignment.
    engagement = models.OneToOneField(
        WorkflowCollectionEngagement, null=True, blank=True, on_delete=models.PROTECT
    )

    class Meta:
        db_table = "workflow_system_collection_assignment"
        verbose_name_plural = "Workflow Collection Assignments"
        ordering = ["workflow_collection", "assigned_on"]
        constraints = [
            models.UniqueConstraint(
                condition=Q(status="ASSIGNED") | Q(status="IN_PROGRESS"),
                fields=["user", "workflow_collection"],
                name="Only one open assignment per workflow collection per user",
            )
        ]

    def __str__(self):
        return "{} - {}".format(self.workflow_collection.name, self.status)

    def clean(self, *args, **kwargs):
        """
        Check assignment constraints.

        (1) We have to ensure that no pre-existing assignment exists with a status
        of ASSIGNED or IN_PROGRESS other than the current instance. This is
        because we want to prevent users from having more than one open
        assignment to any given collection.

        (2) Ensure there is not a mismatch between assignment data and engagement data.
        """
        existing_active_assignments = WorkflowCollectionAssignment.objects.filter(
            Q(status=self.ASSIGNED) | Q(status=self.IN_PROGRESS),
            user=self.user,
            workflow_collection=self.workflow_collection,
        ).exclude(id=self.id)

        if existing_active_assignments and self.status in (
            self.ASSIGNED,
            self.IN_PROGRESS,
        ):
            raise ValidationError(
                "There is an existing active assignment "
                "for this workflow collection/user."
            )

        if self.engagement:
            if self.workflow_collection != self.engagement.workflow_collection:
                raise ValidationError(
                    "The Assignment and Engagement WorkflowCollections "
                    "are not the same."
                )
            elif self.user != self.engagement.user:
                raise ValidationError(
                    "The Assignment and Engagement Users are not the same."
                )

        # User must be active to assign a collection to them
        if not self.user.is_active:
            raise ValidationError(
                {"user": "User must be active to assign a collection to them."}
            )

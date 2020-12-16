import uuid
from datetime import date

from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models import Q

from workflows.models.abstract_models import CreatedModifiedAbstractModel
from workflows.models.engagement import WorkflowCollectionEngagement
from workflows.models.collection import WorkflowCollection


class WorkflowCollectionAssignment(CreatedModifiedAbstractModel):
    """
    Definition of a Workflow Assignment.

    Some workflows can only be accessed via an administrative 
    assignment. The most typical example of this would be 
    a research survey.

    Assignments
    -----------
    id : uuid
        The unique UUID of the record.
    workflow_collection : foreign key
        The WorkflowCollection object associated with the Assignment.
    user : foreign key
        The User being assigned the Workflow.
    assigned_on: datetime
        The date of the Assignment.
    status: charfield
        Whether the assignment is active, stale, or complete
    engagement: foreign key
        Optional Engagement object
    """
    ASSIGNED = 'ASSIGNED'
    IN_PROGRESS = 'IN_PROGRESS'
    CLOSED_INCOMPLETE = 'CLOSED_INCOMPLETE'
    CLOSED_COMPLETE = 'CLOSED_COMPLETE'

    STATUS_CHOICES = (
        (ASSIGNED, "Assigned"),
        (IN_PROGRESS, "In Progress"),
        (CLOSED_INCOMPLETE, "Closed (Incomplete)"),
        (CLOSED_COMPLETE, "Closed (Complete)"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow_collection = models.ForeignKey(
        WorkflowCollection, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    # TODO why is this a datefield and not a datetime
    assigned_on = models.DateField(default=date.today)
    status = models.CharField(choices=STATUS_CHOICES, max_length=17, default=ASSIGNED)
    engagement = models.OneToOneField(
        WorkflowCollectionEngagement,
        null=True, blank=True, on_delete=models.PROTECT)

    class Meta:
        db_table = 'workflow_system_collection_assignment'
        verbose_name_plural = 'Workflow Collection Assignments'
        ordering = ['workflow_collection', 'assigned_on']
        constraints = [
            models.UniqueConstraint(
                condition=Q(status='ASSIGNED') | Q(status='IN_PROGRESS'),
                fields=['user', 'workflow_collection'],
                name="Only one open assignment per workflow collection per user"
            )
        ]

    def __str__(self):
        return "{} - {}".format(
            self.workflow_collection.name,
            self.status)

    def clean(self, *args, **kwargs):
        """
        Ensure that no pre-existing active assignment exists.

        Note that we have to check that the user isn't attempting to
        modify an existing entry - which should be allowed.
        """
        existing_active_assignments = \
            WorkflowCollectionAssignment.objects.filter(
                Q(status=self.ASSIGNED) | Q(status=self.IN_PROGRESS),
                user=self.user,
                workflow_collection=self.workflow_collection
            ).exclude(id=self.id)

        if existing_active_assignments and self.status in (self.ASSIGNED, self.IN_PROGRESS):
            raise ValidationError(
                'There is an existing active assignment '
                'for this workflow collection/user.')

        if self.engagement:
            if self.workflow_collection != self.engagement.workflow_collection:
                raise ValidationError(
                    'The Assignment and Engagement WorkflowCollections '
                    'are not the same.'
                )
            elif self.user != self.engagement.user:
                raise ValidationError(
                    'The Assignment and Engagement Users are not the same.'
                )

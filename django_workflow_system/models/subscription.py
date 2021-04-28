"""Django model definition."""
import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from django_workflow_system.models.abstract_models import CreatedModifiedAbstractModel
from django_workflow_system.models import WorkflowCollection


class WorkflowCollectionSubscription(CreatedModifiedAbstractModel):
    """
    Users who wish to engage in a Workflow Collection on a repeat basis
    can create a WorkflowCollectionSubscription.

    Attributes:
        id (UUIDField): The unique UUID of the record.
        workflow_collection (ForeignKey): The WorkflowCollection object associated with the
                                          subscription.
        user (ForeignKey): The User object who owns the subscription.
        active (BooleanField): Whether or not the subscription is active.

    Notes:
        * By itself, a WorkFlow Collection subscription object isn't of much value.
        * It's value comes from the WorkflowCollectionSubscriptionSchedule objects
        which reference it via foreign and define the details of the
        subscription.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow_collection = models.ForeignKey(
        WorkflowCollection, on_delete=models.PROTECT
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    active = models.BooleanField(default=True)

    class Meta:
        db_table = "workflow_system_collection_subscription"
        unique_together = ["workflow_collection", "user"]
        verbose_name_plural = "Workflow Collection Subscriptions"

    def save(self, *args, **kwargs):
        self.full_clean()
        super(WorkflowCollectionSubscription, self).save(*args, **kwargs)

    def __str__(self):
        return "{} - {}".format(self.user.username, self.workflow_collection.name)

    # User must be active to subscribe a collection to them
    def clean(self):
        if not self.user.is_active:
            raise ValidationError(
                {"user": "User must be active to subscribe to a collection."}
            )

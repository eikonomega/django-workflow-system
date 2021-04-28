"""Django model definition."""
import uuid
from django.db import models

from django_workflow_system.models.abstract_models import CreatedModifiedAbstractModel
from django_workflow_system.models.subscription import WorkflowCollectionSubscription


class WorkflowCollectionSubscriptionSchedule(CreatedModifiedAbstractModel):
    """
    When a user creates a subscription to a Workflow Collection, they also need
    to specify what days of the week (and on what interval of weeks)
    they want to be notified to engage in a subscribed Workflow.

    Notes:
        For each day of the week a user desires a subscription
        notification, one of this objects must be created.

        So, if a user wanted to receive notifications on
        Monday, Wednesday, and Friday they would need to
        have 3 corresponding WorkflowCollectionSubscriptionSchedule
        objects.
    """

    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6
    DAY_OF_WEEK = (
        (MONDAY, "Monday"),
        (TUESDAY, "Tuesday"),
        (WEDNESDAY, "Wednesday"),
        (THURSDAY, "Thursday"),
        (FRIDAY, "Friday"),
        (SATURDAY, "Saturday"),
        (SUNDAY, "Sunday"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow_collection_subscription = models.ForeignKey(
        WorkflowCollectionSubscription, on_delete=models.CASCADE
    )
    time_of_day = models.TimeField()
    day_of_week = models.IntegerField(choices=DAY_OF_WEEK)
    weekly_interval = models.IntegerField(default=1)

    class Meta:
        db_table = "workflow_system_collection_subscription_schedule"
        unique_together = ["workflow_collection_subscription", "day_of_week"]
        verbose_name_plural = "Workflow Collection Subscription Schedules"

    def __str__(self):
        return "{} subscription for {}".format(
            self.workflow_collection_subscription.workflow_collection.name,
            self.workflow_collection_subscription.user.username,
        )

import uuid

from django.contrib.auth.models import User
from django.db import models

from workflows.models.abstract_models import CreatedModifiedAbstractModel
from workflows.models import WorkflowCollection


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
    workflow_collection = models.ForeignKey(WorkflowCollection, on_delete=models.PROTECT)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    active = models.BooleanField(default=True)

    class Meta:
        db_table = 'workflow_system_collection_subscription'
        unique_together = ['workflow_collection', 'user']
        verbose_name_plural = 'Workflow Collection Subscriptions'

    def save(self, *args, **kwargs):
        self.full_clean()
        super(WorkflowCollectionSubscription, self).save(*args, **kwargs)

    def __str__(self):
        return "{} - {}".format(self.user.username, self.workflow_collection.name)


class WorkflowCollectionSubscriptionSchedule(CreatedModifiedAbstractModel):
    """
    When a user creates a subscription to a Workflow Collection, they also need
    to specify what days of the week (and on what interval of weeks)
    they want to be notified to engage in a subscribed Workflow.

    Attributes:
        id (UUIDField): The unique UUID of the record.

        workflow_collection_subscription (ForeignKey): The WorkflowCollectionSubscription object 
                                                       which is being given a schedule.
        time_of_day (TimeField): The User object who owns the subscription.

        day_of_week (IntegerField): An int representing the day of the week the 
                                    user desires to receive subscription notifications.
                                    0 == Monday, 1 == Tuesday, etc
        weekly_interval (IntegerField): On what weekly interval should the user
                                        receive a notification from their subscription.
                                        Defaults to 1 (every week).

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
        (MONDAY, 'Monday'),
        (TUESDAY, 'Tuesday'),
        (WEDNESDAY, 'Wednesday'),
        (THURSDAY, 'Thursday'),
        (FRIDAY, 'Friday'),
        (SATURDAY, 'Saturday'),
        (SUNDAY, 'Sunday'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow_collection_subscription = models.ForeignKey(
        WorkflowCollectionSubscription, on_delete=models.CASCADE)
    time_of_day = models.TimeField()
    day_of_week = models.IntegerField(choices=DAY_OF_WEEK)
    weekly_interval = models.IntegerField(default=1)

    class Meta:
        db_table = 'workflow_system_collection_subscription_schedule'
        unique_together = ["workflow_collection_subscription", "day_of_week"]
        verbose_name_plural = 'Workflow Collection Subscription Schedules'

    def __str__(self):
        return "{} subscription for {}".format(
            self.workflow_collection_subscription.workflow_collection.name,
            self.workflow_collection_subscription.user.username)

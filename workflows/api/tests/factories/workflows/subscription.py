import factory
import datetime

from factory.django import DjangoModelFactory

from .....models import (
    WorkflowCollectionSubscription,
    WorkflowCollectionSubscriptionSchedule,
)


class WorkflowCollectionSubscriptionFactory(DjangoModelFactory):
    class Meta:
        model = WorkflowCollectionSubscription
        django_get_or_create = ("workflow_collection", "user")

    workflow_collection = None  # must be supplied in kwargs
    user = None  # must be supplied in kwargs
    active = True

    @factory.post_generation
    def workflowcollectionsubscriptionschedule_set(self, create, extracted, **kwargs):
        if not create or not extracted:
            return
        for workflowcollectionsubscriptionschedule in extracted:
            WorkflowCollectionSubscriptionScheduleFactory(
                workflow_collection_subscription=self,
                **workflowcollectionsubscriptionschedule,
            )


class WorkflowCollectionSubscriptionScheduleFactory(DjangoModelFactory):
    class Meta:
        model = WorkflowCollectionSubscriptionSchedule
        django_get_or_create = ("workflow_collection_subscription", "day_of_week")

    workflow_collection_subscription = None  # Must be supplied by kwargs
    time_of_day = "12:00:00"
    day_of_week = datetime.datetime.today().weekday()
    weekly_interval = 1


__all__ = [
    "WorkflowCollectionSubscriptionFactory",
    "WorkflowCollectionSubscriptionScheduleFactory",
]

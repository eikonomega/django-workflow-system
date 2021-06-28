import factory
from django.utils import timezone
from factory.django import DjangoModelFactory

from .....models import (
    WorkflowCollectionEngagement,
    WorkflowCollectionEngagementDetail,
)


class WorkflowCollectionEngagementFactory(DjangoModelFactory):
    class Meta:
        model = WorkflowCollectionEngagement

    workflow_collection = None  # must be provided in kwargs
    user = None  # must be provided in kwargs
    started = factory.lazy_attribute(lambda x: timezone.now())

    @factory.post_generation
    def workflowcollectionengagementdetail_set(self, create, extracted, **kwargs):
        if not create or not extracted:
            return
        for workflowcollectionengagementdetail in extracted:
            WorkflowCollectionEngagementDetailFactory(
                workflow_collection_engagement=self,
                **workflowcollectionengagementdetail,
            )


class WorkflowCollectionEngagementDetailFactory(DjangoModelFactory):
    class Meta:
        model = WorkflowCollectionEngagementDetail
        django_get_or_create = ("workflow_collection_engagement", "step")

    workflow_collection_engagement = None  # must be supplied by kwargs
    step = None  # must be supplied by kwargs
    user_responses = None
    started = timezone.now()
    finished = None


__all__ = [
    "WorkflowCollectionEngagementFactory",
    "WorkflowCollectionEngagementDetailFactory",
]

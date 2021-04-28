from datetime import timedelta

import factory
from factory.django import DjangoModelFactory

from django.utils import timezone

from .workflow_collection import WorkflowCollectionFactory
from .....models import WorkflowCollectionRecommendation


class WorkflowCollectionRecommendationFactory(DjangoModelFactory):
    class Meta:
        model = WorkflowCollectionRecommendation

    workflow_collection = factory.SubFactory(WorkflowCollectionFactory)
    user = None  # must be supplied during construction
    start = factory.lazy_attribute(lambda obj: timezone.now() - timedelta(days=3))
    end = None


__all__ = ["WorkflowCollectionRecommendationFactory"]

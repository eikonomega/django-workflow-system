from datetime import timedelta

import factory
from django.utils import timezone

from ...factories import WorkflowCollectionFactory
from .....models import WorkflowCollectionRecommendation


class WorkflowCollectionRecommendationFactory(factory.DjangoModelFactory):
    class Meta:
        model = WorkflowCollectionRecommendation

    workflow_collection = factory.SubFactory(WorkflowCollectionFactory)
    user = None  # must be supplied during construction
    start = factory.lazy_attribute(lambda obj: timezone.now() - timedelta(days=3))
    end = None


__all__ = ["WorkflowCollectionRecommendationFactory"]

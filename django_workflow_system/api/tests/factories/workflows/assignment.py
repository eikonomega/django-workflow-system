from datetime import timedelta

from django.utils import timezone
from factory.django import DjangoModelFactory

from .....models import WorkflowCollectionAssignment


class WorkflowCollectionAssignmentFactory(DjangoModelFactory):
    class Meta:
        model = WorkflowCollectionAssignment
        django_get_or_create = ("start", "workflow_collection", "user")

    workflow_collection = None  # must be supplied in kwargs
    user = None  # must be supplied in kwargs
    engagement = None  # optional
    start = timezone.now()
    end = timezone.now() + timedelta(days=10)
    status = WorkflowCollectionAssignment.ASSIGNED


__all__ = ["WorkflowCollectionAssignmentFactory"]

from datetime import timedelta

from django.utils import timezone
from factory.django import DjangoModelFactory

from .....models import WorkflowCollectionAssignment


class WorkflowCollectionAssignmentFactory(DjangoModelFactory):
    class Meta:
        model = WorkflowCollectionAssignment
        django_get_or_create = ("assigned_on", "workflow_collection", "user")

    workflow_collection = None  # must be supplied in kwargs
    user = None  # must be supplied in kwargs
    engagement = None  # optional
    assigned_on = timezone.now().date()
    expiration = timezone.now().date() + timedelta(days=10)
    status = WorkflowCollectionAssignment.ASSIGNED


__all__ = ["WorkflowCollectionAssignmentFactory"]

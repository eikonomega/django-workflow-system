import django_workflow_system.models as models
from factory.django import DjangoModelFactory


class WorkflowCollectionImageTypeFactory(DjangoModelFactory):
    class Meta:
        model = models.WorkflowCollectionImageType
        django_get_or_create = ["type"]


class WorkflowCollectionImageFactory(DjangoModelFactory):
    class Meta:
        model = models.WorkflowCollectionImage
        django_get_or_create = ["image", "type"]


__all__ = ["WorkflowCollectionImageTypeFactory", "WorkflowCollectionImageFactory"]

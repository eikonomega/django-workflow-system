import django_workflow_system.models as models
from factory.django import DjangoModelFactory


class WorkflowImageTypeFactory(DjangoModelFactory):
    class Meta:
        model = models.WorkflowImageType
        django_get_or_create = ["type"]


class WorkflowImageFactory(DjangoModelFactory):
    class Meta:
        model = models.WorkflowImage
        django_get_or_create = ["image", "type"]


__all__ = ["WorkflowImageTypeFactory", "WorkflowImageFactory"]

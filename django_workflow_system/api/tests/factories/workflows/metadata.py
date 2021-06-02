import factory
from factory.django import DjangoModelFactory

import django_workflow_system.models as models


class WorkflowMetadataFactory(DjangoModelFactory):
    class Meta:
        model = models.WorkflowMetadata
        django_get_or_create = ("name",)

    name = factory.sequence(lambda n: "datagroup_{}".format(n))
    description = factory.Faker("paragraph")


__all__ = ["WorkflowMetadataFactory"]

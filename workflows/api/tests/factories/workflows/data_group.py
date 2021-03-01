import factory
from factory.django import DjangoModelFactory

import workflows.models as models


class WorkflowStepDataGroupFactory(DjangoModelFactory):
    class Meta:
        model = models.WorkflowStepDataGroup
        django_get_or_create = ('name',)

    name = factory.sequence(lambda n: "datagroup_{}".format(n))
    description = factory.Faker('paragraph')


__all__ = ["WorkflowStepDataGroupFactory"]

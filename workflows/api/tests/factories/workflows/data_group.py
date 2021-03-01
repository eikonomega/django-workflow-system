import factory


import workflows.models as models


class WorkflowStepDataGroupFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.WorkflowStepDataGroup
        django_get_or_create = ('name',)

    name = factory.sequence(lambda n: "datagroup_{}".format(n))
    description = factory.Faker('paragraph')


__all__ = ["WorkflowStepDataGroupFactory"]

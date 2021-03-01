import factory
from django.conf import settings
from factory.django import DjangoModelFactory

import workflows.models as models
from .step import WorkflowStepFactory
from .authors import AuthorFactory
from ..user import UserFactory


class WorkflowFactory(DjangoModelFactory):
    class Meta:
        model = models.Workflow
        exclude = ("steps",)

    name = factory.sequence(lambda n: f"workflow name {n}")
    code = factory.sequence(lambda n: f"workflow_code_{n}")
    version = 1
    image = f"{settings.MEDIA_ROOT}/wumbo.jpg"
    author = factory.SubFactory(AuthorFactory)
    created_by = factory.SubFactory(UserFactory, is_staff=True)

    @factory.post_generation
    def workflowstep_set(self, create, extracted, **kwargs):
        if not create or not extracted:
            return
        for step in extracted:
            if isinstance(step, dict):
                WorkflowStepFactory.create(workflow=self, **step)
            elif isinstance(step, models.WorkflowStep):
                step.workflow = self
            else:
                raise TypeError("step must be a dict or WorkflowStep")


__all__ = ["WorkflowFactory"]

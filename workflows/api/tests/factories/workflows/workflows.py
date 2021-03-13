import factory
from factory.django import DjangoModelFactory

from workflows.models import Workflow, WorkflowStep
from .step import WorkflowStepFactory
from .authors import AuthorFactory
from ..user import UserFactory


class WorkflowFactory(DjangoModelFactory):
    class Meta:
        model = Workflow
        exclude = ("steps",)

    name = factory.sequence(lambda n: f"workflow name {n}")
    code = factory.sequence(lambda n: f"workflow_code_{n}")
    version = 1
    image = f"wumbo.jpg"
    author = factory.SubFactory(AuthorFactory)
    created_by = factory.SubFactory(UserFactory, is_staff=True)

    @factory.post_generation
    def workflowstep_set(self, create, extracted, **kwargs):
        if not create or not extracted:
            return
        for step in extracted:
            if isinstance(step, dict):
                WorkflowStepFactory.create(workflow=self, **step)
            elif isinstance(step, WorkflowStep):
                step.workflow = self
            else:
                raise TypeError("step must be a dict or WorkflowStep")


__all__ = ["WorkflowFactory"]

import factory
from factory.django import DjangoModelFactory

from django_workflow_system.models import Workflow, WorkflowStep, WorkflowMetadata
from .step import WorkflowStepFactory
from .authors import AuthorFactory
from .metadata import WorkflowMetadataFactory
from ..user import UserFactory


class WorkflowFactory(DjangoModelFactory):
    class Meta:
        model = Workflow
        exclude = ("steps",)

    name = factory.sequence(lambda n: f"workflow name {n}")
    code = factory.sequence(lambda n: f"workflow_code_{n}")
    version = 1
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

    @factory.post_generation
    def metadata(self, create, extracted, **kwargs):
        if not create or not extracted:
            return
        for metadata in extracted:
            if isinstance(metadata, WorkflowMetadata):
                self.metadata.add(metadata)
            elif isinstance(metadata, str):
                self.metadata.add(
                    WorkflowMetadataFactory(name=metadata, description="Eh, Whatever")
                )


__all__ = ["WorkflowFactory"]

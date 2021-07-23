import factory
from factory.django import DjangoModelFactory

import django_workflow_system.models as models
from .workflows import WorkflowFactory
from .metadata import WorkflowMetadataFactory
from ..user import UserFactory


class WorkflowCollectionFactory(DjangoModelFactory):
    """
    :param workflow_set: an iterable of Workflows to add to this collection.
    :param dependency_group_set: an iterable of dicts representing
            the dependency groups to be created
    """

    class Meta:
        model = models.WorkflowCollection

    name = factory.sequence(lambda n: "workflow collection name {}".format(n))
    code = factory.sequence(lambda n: "workflow_collection_code_{}".format(n))
    description = "Blank"
    ordered = True
    version = 1
    created_by = factory.SubFactory(UserFactory, is_staff=True)
    assignment_only = False
    active = True
    category = "ACTIVITY"
    recommendable = False

    @factory.post_generation
    def workflow_set(self, create, extracted, **kwargs):
        if not create or not extracted:
            return
        for i, workflow in enumerate(extracted):
            # we create a linking object that kinda stays inaccessible
            if isinstance(workflow, dict):
                _WorkflowCollectionMemberFactory.create(
                    workflow_collection=self,
                    workflow=WorkflowFactory(**workflow),
                    order=i + 1,
                )
            elif isinstance(workflow, models.Workflow):
                _WorkflowCollectionMemberFactory.create(
                    workflow_collection=self, workflow=workflow, order=i + 1
                )
            else:
                raise TypeError("unsupported element in workflows list")

    @factory.post_generation
    def workflowstepdependencygroup_set(self, create, extracted, **kwargs):
        if not create or not extracted:
            return
        for dependency_group in extracted:
            if isinstance(dependency_group, dict):
                if isinstance(dependency_group["workflow_step"], dict):
                    dependency_group[
                        "workflow_step"
                    ] = models.WorkflowStep.objects.get_or_create(
                        **dependency_group["workflow_step"]
                    )[
                        0
                    ]
                _WorkflowStepDependencyGroup(
                    workflow_collection=self,
                    **dependency_group,
                )

    @factory.post_generation
    def metadata(self, create, extracted, **kwargs):
        if not create or not extracted:
            return
        for metadata in extracted:
            if isinstance(metadata, models.WorkflowMetadata):
                self.metadata.add(metadata)
            elif isinstance(metadata, str):
                self.metadata.add(
                    WorkflowMetadataFactory(name=metadata, description="Eh, Whatever")
                )


class _WorkflowCollectionMemberFactory(DjangoModelFactory):
    """
    This factory should never be invoked directly.
    Use `WorkflowCollectionFactory.create(workflows=[workflow1, workflow2,...])`
    """

    class Meta:
        model = models.WorkflowCollectionMember

    workflow = None  # must be provided in args
    workflow_collection = None  # must be provided in kwargs
    order = factory.Sequence(lambda n: int(n + 1))


class _WorkflowStepDependencyGroup(DjangoModelFactory):
    class Meta:
        model = models.WorkflowStepDependencyGroup

    workflow_collection = None  # Must be supplied in kwargs
    workflow_step = None  # Must be supplied in kwargs

    @factory.post_generation
    def workflowstepdependencydetail_set(self, create, extracted, **kwargs):
        if not create or not extracted:
            return
        for dependency in extracted:
            if isinstance(dependency["dependency_step"], dict):
                dependency[
                    "dependency_step"
                ] = models.WorkflowStep.objects.get_or_create(
                    **dependency["dependency_step"]
                )[
                    0
                ]
            _WorkflowStepDependencyDetailFactory(
                dependency_group=self,
                **dependency,
            )


class _WorkflowStepDependencyDetailFactory(DjangoModelFactory):
    class Meta:
        model = models.WorkflowStepDependencyDetail

    dependency_group = None  # Must be supplied in kwargs
    dependency_step = None  # Must be supplied in kwargs
    required_response = None  # Must be supplied in kwargs


__all__ = ["WorkflowCollectionFactory"]

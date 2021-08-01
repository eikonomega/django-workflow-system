import factory
from factory.django import DjangoModelFactory

import django_workflow_system.models as models
from .metadata import WorkflowMetadataFactory


class WorkflowStepUITemplateFactory(DjangoModelFactory):
    class Meta:
        model = models.WorkflowStepUITemplate
        django_get_or_create = ("name",)

    name = factory.sequence(lambda n: f"step_code_name_{n}")


class WorkflowStepFactory(DjangoModelFactory):
    class Meta:
        model = models.WorkflowStep
        django_get_or_create = ("workflow", "code")

    workflow = None  # must be supplied in kwargs
    code = factory.sequence(lambda n: "step_code_{}".format(n))
    order = factory.sequence(lambda n: int(n))
    ui_template = factory.SubFactory(WorkflowStepUITemplateFactory)

    @factory.post_generation
    def workflowsteptext_set(self, create, extracted, **kwargs):
        if not create or not extracted:
            return
        for text in extracted:
            _WorkflowStepTextFactory.create(workflow_step=self, **text)

    @factory.post_generation
    def workflowstepimage_set(self, create, extracted, **kwargs):
        if not create or not extracted:
            return
        for image in extracted:
            _WorkflowStepImageFactory.create(workflow_step=self, **image)

    @factory.post_generation
    def workflowstepaudio_set(self, create, extracted, **kwargs):
        if not create or not extracted:
            return
        for audio in extracted:
            _WorkflowStepAudioFactory.create(workflow_step=self, **audio)

    @factory.post_generation
    def workflowstepuserinput_set(self, create, extracted, **kwargs):
        if not create or not extracted:
            return
        for input in extracted:
            _WorkflowStepUserInputFactory.create(workflow_step=self, **input)

    @factory.post_generation
    def workflowstepexternallink_set(self, create, extracted, **kwargs):
        if not create or not extracted:
            return
        for input in extracted:
            _WorkflowStepExternalLinkFactory.create(workflow_step=self, **input)

    @factory.post_generation
    def metadata(self, create, extracted, **kwargs):
        if not create or not extracted:
            return
        for metadata in extracted:
            if isinstance(metadata, dict):
                self.metadata.add(WorkflowMetadataFactory(**metadata))
            elif isinstance(metadata, models.WorkflowMetadata):
                self.metadata.add(metadata)
            else:
                raise TypeError("metadata must be a dict or WorkflowMetadata")


class _WorkflowStepTextFactory(DjangoModelFactory):
    class Meta:
        model = models.WorkflowStepText
        django_get_or_create = ["workflow_step", "ui_identifier"]

    workflow_step = None  # required in kwargs
    ui_identifier = factory.sequence(lambda n: f"text_{n}")
    text = factory.Faker("paragraph")


class _WorkflowStepExternalLinkFactory(DjangoModelFactory):
    class Meta:
        model = models.WorkflowStepExternalLink
        django_get_or_create = ["workflow_step", "ui_identifier"]

    workflow_step = None
    ui_identifier = factory.sequence(lambda n: f"external_link_{n}")
    link = factory.Faker("https://www.google.com")


class _WorkflowStepImageFactory(DjangoModelFactory):
    class Meta:
        model = models.WorkflowStepImage
        django_get_or_create = ["workflow_step", "ui_identifier"]

    workflow_step = None  # required in kwargs
    ui_identifier = factory.sequence(lambda n: f"image_{n}")
    url = factory.Faker("file_name", extension="png")


class _WorkflowStepVideoFactory(DjangoModelFactory):
    class Meta:
        model = models.WorkflowStepVideo
        django_get_or_create = ["workflow_step", "ui_identifier"]

    workflow_step = None  # required in kwargs
    ui_identifier = factory.sequence(lambda n: f"video_{n}")
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"


class _WorkflowStepAudioFactory(DjangoModelFactory):
    class Meta:
        model = models.WorkflowStepAudio
        django_get_or_create = ["workflow_step", "ui_identifier"]

    workflow_step = None  # required in kwargs
    ui_identifier = factory.sequence(lambda n: f"audio_{n}")
    url = factory.Faker("file_name", extension="mp3")


class _WorkflowStepUserInputTypeFactory(DjangoModelFactory):
    class Meta:
        model = models.WorkflowStepUserInputType

    name = factory.sequence(lambda n: "Question Type {}".format(n))
    json_schema = {}
    example_specification = {}


class _WorkflowStepUserInputFactory(DjangoModelFactory):
    class Meta:
        model = models.WorkflowStepUserInput
        django_get_or_create = ["workflow_step", "ui_identifier", "type"]

    workflow_step = None  # required in kwargs
    ui_identifier = factory.sequence(lambda n: f"input_{n}")
    required = False
    type = factory.SubFactory(_WorkflowStepUserInputTypeFactory)
    specification = {}


__all__ = ["WorkflowStepUITemplateFactory", "WorkflowStepFactory"]

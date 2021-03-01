import factory
from factory.django import DjangoModelFactory

import workflows.models as models
from .data_group import WorkflowStepDataGroupFactory
from .json_schema import JSONSchemaFactory


class WorkflowStepUITemplateFactory(DjangoModelFactory):
    class Meta:
        model = models.WorkflowStepUITemplate
        django_get_or_create = ("name",)

    name = factory.sequence(lambda n: "step_code_name_{}".format(n))


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
    def workflowstepinput_set(self, create, extracted, **kwargs):
        if not create or not extracted:
            return
        for input in extracted:
            _WorkflowStepInputFactory.create(workflow_step=self, **input)

    @factory.post_generation
    def data_groups(self, create, extracted, **kwargs):
        if not create or not extracted:
            return
        for data_group in extracted:
            if isinstance(data_group, dict):
                self.data_groups.add(WorkflowStepDataGroupFactory(**data_group))
            elif isinstance(data_group, models.WorkflowStepDataGroup):
                self.data_groups.add(data_group)
            else:
                raise TypeError("data_group must be a dict or WorkflowStepDataGroup")


class _WorkflowStepTextFactory(DjangoModelFactory):
    class Meta:
        model = models.WorkflowStepText
        django_get_or_create = ["workflow_step", "ui_identifier"]

    workflow_step = None  # required in kwargs
    ui_identifier = factory.sequence(lambda n: "text_{}".format(n))
    content = factory.Faker("paragraph")
    storage_value = factory.Sequence(lambda n: int(n + 1))


class _WorkflowStepImageFactory(DjangoModelFactory):
    class Meta:
        model = models.WorkflowStepImage
        django_get_or_create = ["workflow_step", "ui_identifier"]

    workflow_step = None  # required in kwargs
    ui_identifier = factory.sequence(lambda n: "image_{}".format(n))
    url = factory.Faker("file_name", extension="png")


class _WorkflowStepVideoFactory(DjangoModelFactory):
    class Meta:
        model = models.WorkflowStepVideo
        django_get_or_create = ["workflow_step", "ui_identifier"]

    workflow_step = None  # required in kwargs
    ui_identifier = factory.sequence(lambda n: "video_{}".format(n))
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"


class _WorkflowStepAudioFactory(DjangoModelFactory):
    class Meta:
        model = models.WorkflowStepAudio
        django_get_or_create = ["workflow_step", "ui_identifier"]

    workflow_step = None  # required in kwargs
    ui_identifier = factory.sequence(lambda n: "audio_{}".format(n))
    url = factory.Faker("file_name", extension="mp3")


class _WorkflowStepInputFactory(DjangoModelFactory):
    class Meta:
        model = models.WorkflowStepInput
        django_get_or_create = ["workflow_step", "ui_identifier"]

    workflow_step = None  # required in kwargs
    ui_identifier = factory.sequence(lambda n: "input_{}".format(n))
    content = factory.Faker("sentence")
    required = False
    response_schema = factory.SubFactory(JSONSchemaFactory)


__all__ = ["WorkflowStepUITemplateFactory", "WorkflowStepFactory"]

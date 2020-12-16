import uuid

from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.validators import MinValueValidator
from django.db import models
from jsonschema import Draft7Validator, SchemaError

from workflows.models.abstract_models import CreatedModifiedAbstractModel
from workflows.models.collection import (
    WorkflowCollection, WorkflowCollectionMember)
from workflows.models.data_group import WorkflowStepDataGroup
from workflows.models.json_schema import JSONSchema
from workflows.models.workflow import Workflow


def workflow_step_media_folder(instance, filename):
    return 'workflows/workflows/{}/steps/{}/{}.{}'.format(
        instance.workflow_step.workflow.id,
        instance.workflow_step_id,
        instance.ui_identifier,
        filename.rpartition('.')[2])


class WorkflowStepUITemplate(CreatedModifiedAbstractModel):
    """
    User interface template specification for Workflows.

    While the back-end of the application doesn't care
    about the design of the user interface, it does need to
    indicate to various potential interfaces which design template a
    Workflow author intended to be used for a given Workflow step.

    Attributes
    ----------
    id: uuid
        The UUID for the database record.
    name: CharField
        The name of the step template

    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, unique=True)

    class Meta:
        db_table = 'workflow_system_step_ui_template'
        verbose_name_plural = 'Workflow UI Templates'

    def __str__(self):
        return self.name


class WorkflowStep(CreatedModifiedAbstractModel):
    """
    Every workflow is comprised of one or more "steps" that a user
    must complete in order to finish it.

    - Each Step MAY have one or more associated StepText objects.
    - Each Step MAY have one or more associated StepVideo objects.
    - Each Step MAY have one or more associated StepImage objects.
    - Each Step MAY have one or more associated StepAudio objects.
    - Each Step MAY have one or more associated StepInput objects.

    Attributes
    ----------

    id : uuid
        The UUID for the database record.
    workflow : UUID (foreign key)
        The Workflow associated with the step
    code : CharField
        The identifying code of the step
    order : PositiveIntergerField
        The order in which the step occurs
    ui_template : UUID (foreign key)
        The ui template associated with the step
    data_groups : Many to many relationship
        A list of workflow step data groups this step belongs to

    Notes
    -----
    There is some unusual syntax on "unique" constraints for this model that
    developers may not be used to seeing. Essentially, we specify
    that there are two separate uniqueness contraints to fulfill:
        * workflow/code combination must be unique
        * workflow/order combination must be unique
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE)
    code = models.CharField(max_length=200)
    order = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    ui_template = models.ForeignKey(
        WorkflowStepUITemplate,
        on_delete=models.PROTECT)
    data_groups = models.ManyToManyField(WorkflowStepDataGroup, blank=True)

    class Meta:
        db_table = 'workflow_system_step'
        unique_together = [["workflow", "code"], ["workflow", "order"]]
        verbose_name_plural = 'Workflow Steps'
        ordering = ['-workflow', 'order']

    def __str__(self):
        return "{} - {}".format(
            self.workflow.name,
            self.code)


class WorkflowStepDependencyGroup(CreatedModifiedAbstractModel):
    """
    This model allows multiple step dependencies to be grouped together as a
    logical set of dependencies.

    Attributes
    ----------
    id : uuid
        The unique UUID for the database record.
    workflow_collection : UUID (foreign key)
       The Workflow Collection of the Step's Workflow
    workflow_step : UUID (foreign key)
        The WorkflowStep object that will have a dependency.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow_collection = models.ForeignKey(
        WorkflowCollection, on_delete=models.CASCADE)
    workflow_step = models.ForeignKey(WorkflowStep, on_delete=models.CASCADE)

    class Meta:
        db_table = "workflow_system_step_dependency_group"
        verbose_name_plural = 'Workflow Step Dependency Groups'

    def __str__(self):
        return "{} - {}".format(
            self.workflow_step.code,
            self.workflow_collection.code)

    def clean(self):
        """
        Provide custom validation for the following:
        * Step's workflow must be a member of the Workflow Collection
        """
        try:
            WorkflowCollectionMember.objects.get(
                workflow_collection=self.workflow_collection,
                workflow=self.workflow_step.workflow)
        except ObjectDoesNotExist:
            raise ValidationError(
                "Step's workflow must be a member of the Workflow Collection.")


class WorkflowStepDependencyDetail(CreatedModifiedAbstractModel):
    """
    This model represents a single dependency specification
    within a dependency group.

    Attributes
    ----------
    id : uuid
        The unique UUID for the database record.
    dependency_group : UUID (foreign key)
        The Dependency Group the Step Dependency belongs to.
    dependency_step : UUID (foreign key)
        The WorkflowStep object that is being depended on.
    required_response : JSONField
        The user response that is required for the dependency to be
        considered fulfilled.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dependency_group = models.ForeignKey(
        WorkflowStepDependencyGroup, on_delete=models.CASCADE)
    dependency_step = models.ForeignKey(WorkflowStep, on_delete=models.CASCADE)
    required_response = models.JSONField()

    class Meta:
        db_table = "workflow_system_step_dependency_detail"
        verbose_name_plural = 'Workflow Step Dependency Details'
        unique_together = ('dependency_group', 'dependency_step')

    def __str__(self):
        return "{} -> {}".format(
            self.dependency_group.workflow_step.code,
            self.dependency_group.workflow_collection.code,
            self.dependency_step.code)

    def clean(self):
        """
        Provide custom validation for the following:

        * required_response must be a valid JSON Schema
        * You cannot create a circular dependency.
        * dependency_step's Workflow must be a member of the
            dependency_group's Workflow Collection
        * If the steps belong to the same Workflow then the given step
            cannot depend on a step that comes after it in the Workflow.
        * If the steps don't belong to the same Workflow then the
            given step's Workflow cannot come before the depended on
            step's Workflow in the Collection.
        """
        dependency_group = self.dependency_group
        dependency_step = self.dependency_step

        # required_response must be a valid JSON Schema
        try:
            Draft7Validator.check_schema(self.required_response)
        except SchemaError as error:
            raise ValidationError({
                'required_response': (
                    'There is something wrong in your schema definition. '
                    'Details {}'.format(error))})

        # dependency_step's Workflow must be a
        # member of the dependency_group's Workflow Collection
        try:
            dependency_step_workflow = \
                WorkflowCollectionMember.objects.get(
                    workflow_collection=dependency_group.workflow_collection,
                    workflow=dependency_step.workflow)
        except ObjectDoesNotExist:
            raise ValidationError("dependency_step's Workflow must be a "
                                  "member of the dependency_group's "
                                  "Workflow Collection")
        else:
            dependency_step_workflow_order = dependency_step_workflow.order

        if dependency_step.workflow == dependency_group.workflow_step.workflow:
            # You cannot create a circular dependency.
            if dependency_step == dependency_group.workflow_step:
                raise ValidationError(
                    'The value of dependency_step cannot be equal to the '
                    'value of workflow_step in the associated dependency_'
                    'group. This would represent a circular dependency.')
            # The Dependency Step order cannot be later than the Workflow Step
            elif dependency_step.order > dependency_group.workflow_step.order:
                raise ValidationError(
                    'Dependency Step order cannot be later '
                    'than the Workflow Step order.')
        # Dependency Step Workflow Order cannot be later
        # than the Workflow Step Workflow order
        else:
            workflow_step_workflow_order = \
                WorkflowCollectionMember.objects.get(
                    workflow_collection=dependency_group.workflow_collection,
                    workflow=dependency_group.workflow_step.workflow).order

            if dependency_step_workflow_order > \
                    workflow_step_workflow_order:
                raise ValidationError('Dependency Step Workflow Order '
                                      'cannot be later than the Workflow '
                                      'Step Workflow order.')


class WorkflowStepText(CreatedModifiedAbstractModel):
    """
    Text objects assigned to a WorkflowStep.

    A WorkFlow author is allowed to specify an arbitrary number
    of text elements to a given WorkflowStep.

    Attributes
    ----------
    id : uuid
        The unique UUID for the database record.
    workflow_step : ForeignKey
        The WorkflowStep object that will own this object.
    ui_identifier : CharField
        A simple string which is used to indicate 
        to a user interface where to display this object
        within a template.
    content : CharField
        The actual text.
    storage_value: PositiveIntergerField
        The value that will be stored, in place of direct user input.
        This is used when multiple WorkflowStepInputs are used to represent single-choice options.

    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow_step = models.ForeignKey(
        WorkflowStep,
        on_delete=models.CASCADE)
    ui_identifier = models.CharField(max_length=200)
    content = models.CharField(max_length=500)
    storage_value = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'workflow_system_step_text'
        unique_together = ["workflow_step", "ui_identifier"]
        verbose_name_plural = 'Workflow Step Texts'

    def __str__(self):
        return self.ui_identifier


class WorkflowStepImage(CreatedModifiedAbstractModel):
    """
    Image objects assigned to a WorkflowStep.

    A WorkFlow author is allowed to specify an arbitrary number
    of images elements to a given WorkflowStep.

    Attributes
    -----------
    id : uuid
        The unique UUID for the database record.
    workflow_step: ForeignKey
        The Workflow Step associated with the Image
    ui_identifier: CharField
        A simple string which is used to indicate 
        to a user interface where to display this object
        within a template.
    url: ImageField
        The image location

    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow_step = models.ForeignKey(
        WorkflowStep,
        on_delete=models.PROTECT)
    ui_identifier = models.CharField(max_length=200)
    url = models.ImageField(
        upload_to=workflow_step_media_folder,
        max_length=200)

    class Meta:
        db_table = 'workflow_system_step_image'
        verbose_name_plural = "Workflow Step Images"
        unique_together = ["workflow_step", "ui_identifier"]

    def __str__(self):
        return self.ui_identifier


class WorkflowStepVideo(CreatedModifiedAbstractModel):
    """
    Video objects assigned to a WorkflowStep.

    A WorkFlow author is allowed to specify an arbitrary number
    of video elements to a given WorkflowStep.

    Attributes
    -----------
    id: uuid
        The UUID for the database record.
    workflow_step: UUID(ForeignKey)
        The Workflow Step associated with the video
    ui_identifier: CharField
        A simple string which is used to indicate 
        to a user interface where to display this object
        within a template.
    preview_image_url: URLField
        The location of an image to display before the video plays
    url: URLField
        The video location

    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow_step = models.ForeignKey(
        WorkflowStep,
        on_delete=models.PROTECT)
    ui_identifier = models.CharField(max_length=200)
    url = models.URLField()

    class Meta:
        db_table = 'workflow_system_step_video'
        verbose_name_plural = "Workflow Step Videos"
        unique_together = ['workflow_step', 'ui_identifier']

    def __str__(self):
        return self.ui_identifier


class WorkflowStepAudio(CreatedModifiedAbstractModel):
    """
    Audio objects assigned to a WorkflowStep.

    A WorkFlow author is allowed to specify an arbitrary number
    of audio elements to a given WorkflowStep.

    Attributes
    -----------
    id: uuid
        The UUID for the database record.
    workflow_step: UUID(ForeignKey)
        The Workflow Step associated with the audio
    ui_identifier: CharField
        A simple string which is used to indicate
        to a user interface where to display this object
        within a template.
    url: FileField
        The location of the audio

    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow_step = models.ForeignKey(
        WorkflowStep,
        on_delete=models.PROTECT)
    ui_identifier = models.CharField(max_length=200)
    url = models.FileField(
        upload_to=workflow_step_media_folder,
        max_length=200)

    class Meta:
        db_table = 'workflow_system_step_audio'
        verbose_name_plural = "Workflow Step Audio"
        unique_together = ['workflow_step', 'ui_identifier']

    def __str__(self):
        return self.ui_identifier


class WorkflowStepInput(CreatedModifiedAbstractModel):
    """
    Question objects assigned to a WorkflowStep.

    A WorkFlow author is allowed to specify an arbitrary number
    of question elements to a given WorkflowStep.

    Attributes
    ----------
    id : uuid
        The unique UUID for the database record.
    workflow_step : ForeignKey
        The WorkflowStep object that will own this object.
    ui_identifier : CharField
        A simple string which is used to indicate
        to a user interface where to display this object
        within a template.
    content : CharField
        The actual text of the question.
    required: bool
        True if a value is required for this input in the response JSON
    response_schema : ForeignKey
        An JSON Schema specification used to validate/reject user responses.

    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow_step = models.ForeignKey(
        WorkflowStep,
        on_delete=models.CASCADE)
    ui_identifier = models.CharField(max_length=200)
    content = models.CharField(max_length=500)
    required = models.BooleanField()
    response_schema = models.ForeignKey(
        JSONSchema,
        on_delete=models.PROTECT)

    class Meta:
        db_table = 'workflow_system_step_input'
        unique_together = ["workflow_step", "ui_identifier"]
        verbose_name_plural = 'Workflow Step Inputs'

    def __str__(self):
        return self.ui_identifier

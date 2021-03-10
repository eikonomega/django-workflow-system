"""Django model definition."""
import uuid

from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.validators import MinValueValidator
from django.db import models
from jsonschema import Draft7Validator, SchemaError

from workflows.models.abstract_models import CreatedModifiedAbstractModel
from workflows.models.collection import WorkflowCollection
from workflows.models.collection_member import WorkflowCollectionMember
from workflows.models.data_group import WorkflowStepDataGroup
from workflows.models.json_schema import JSONSchema
from workflows.models.workflow import Workflow


def workflow_step_media_folder(instance, filename):
    return "workflows/workflows/{}/steps/{}/{}.{}".format(
        instance.workflow_step.workflow.id,
        instance.workflow_step_id,
        instance.ui_identifier,
        filename.rpartition(".")[2],
    )


class WorkflowStepUITemplate(CreatedModifiedAbstractModel):
    """
    User interface template specification for Workflows.

    While the back-end of the application doesn't care
    about the design of the user interface, it does need to
    indicate to various potential interfaces which design template a
    Workflow author intended to be used for a given Workflow step.

    That is what this model is for.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(
        max_length=200, unique=True, help_text="The name of the template."
    )

    class Meta:
        db_table = "workflow_system_step_ui_template"
        verbose_name_plural = "Workflow UI Templates"

    def __str__(self):
        return self.name


class WorkflowStep(CreatedModifiedAbstractModel):
    """
    Every workflow is comprised of one or more "steps".

    - Each Step MAY have one or more associated StepText objects.
    - Each Step MAY have one or more associated StepVideo objects.
    - Each Step MAY have one or more associated StepImage objects.
    - Each Step MAY have one or more associated StepAudio objects.
    - Each Step MAY have one or more associated StepInput objects.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow = models.ForeignKey(
        Workflow,
        on_delete=models.CASCADE,
        help_text="The workflow associated with the step.",
    )
    # TODO: GH Issue 26
    code = models.CharField(
        max_length=200,
        help_text="An identifier for programmatically referencing this step.",
    )
    order = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text="The order in which this step occurs in the workflow.",
    )
    ui_template = models.ForeignKey(
        WorkflowStepUITemplate,
        on_delete=models.PROTECT,
        help_text="The UI template associated with the step.",
    )
    data_groups = models.ManyToManyField(
        WorkflowStepDataGroup,
        blank=True,
        help_text="A list of data groups that this step is associated with.",
    )

    class Meta:
        db_table = "workflow_system_step"
        unique_together = [["workflow", "code"], ["workflow", "order"]]
        verbose_name_plural = "Workflow Steps"
        ordering = ["-workflow", "order"]

    def __str__(self):
        return "{} - {}".format(self.workflow.name, self.code)


class WorkflowStepDependencyGroup(CreatedModifiedAbstractModel):
    """
    Dependency groups allow clients to conditionally organize steps.

    For this model, the client must specify what workflow step
    the dependency group should be created for. And, since a given
    workflow step could be a part of multiple collections, the
    relavant collection must also be referenced.

    After all, it is possible that you would want to establish a
    dependency for a given step in one collection, but not another.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow_collection = models.ForeignKey(
        WorkflowCollection, on_delete=models.CASCADE
    )
    workflow_step = models.ForeignKey(WorkflowStep, on_delete=models.CASCADE)

    class Meta:
        db_table = "workflow_system_step_dependency_group"
        verbose_name_plural = "Workflow Step Dependency Groups"

    def __str__(self):
        return "{} - {}".format(self.workflow_step.code, self.workflow_collection.code)

    def clean(self):
        """Ensure the specified step exists in the specified collection."""
        try:
            WorkflowCollectionMember.objects.get(
                workflow_collection=self.workflow_collection,
                workflow=self.workflow_step.workflow,
            )
        except ObjectDoesNotExist:
            raise ValidationError(
                {
                    "workflow_step": "Step's workflow must be a member of the Workflow Collection."
                }
            )


class WorkflowStepDependencyDetail(CreatedModifiedAbstractModel):
    """
    This model registers a specific dependency for a WorkflowStepDependencyGroup.

    The general idea here is that when you register a dependency you are telling
    the system that a given step should only be served to a user if the dependency
    conditions are met.

    For example, let's say you were building a medical workflow and the first step of
    the question obtains the gender of the patient. Depending on that answer, you
    may need to display/hide different following steps.

    We do this by creating instances of this model.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dependency_group = models.ForeignKey(
        WorkflowStepDependencyGroup,
        on_delete=models.CASCADE,
        help_text="The dependency group that this record will be added to. When you have more than one record in a group, ALL conditions must be must.",
    )
    dependency_step = models.ForeignKey(
        WorkflowStep,
        on_delete=models.CASCADE,
        help_text="The step that has the user response that needs to be evaluated.",
    )
    required_response = models.JSONField(
        help_text="The response required for the dependency to be considered fulfilled."
    )

    class Meta:
        db_table = "workflow_system_step_dependency_detail"
        verbose_name_plural = "Workflow Step Dependency Details"
        unique_together = ("dependency_group", "dependency_step")

    def __str__(self):
        return "{} -> {}".format(
            self.dependency_group.workflow_step.code,
            self.dependency_group.workflow_collection.code,
            self.dependency_step.code,
        )

    def clean(self):
        """
        Perform a variety of validation tasks.

        1. `required_response` must be a valid JSON Schema
        2.  You cannot create a circular dependency.
        3. The Workflow of the Step specified here MUST belong also exist
           as a member of the Collection specified in the dependency group.
        4. If the steps belong to the same Workflow then the step specified
           MUST have an order below the step specified in the dependency group.
        5. If the steps don't belong to the same Workflow then the
           Workflow of the Step specified here MUST come before the
           Workflow of the Step specified in the dependency group.
            step's Workflow in the Collection.
        """
        dependency_group = self.dependency_group
        dependency_step = self.dependency_step

        # required_response must be a valid JSON Schema
        try:
            Draft7Validator.check_schema(self.required_response)
        except SchemaError as error:
            raise ValidationError(
                {
                    "required_response": (
                        "There is something wrong in your schema definition. "
                        "Details {}".format(error)
                    )
                }
            )

        # dependency_step's Workflow must be a
        # member of the dependency_group's Workflow Collection
        try:
            dependency_step_workflow = WorkflowCollectionMember.objects.get(
                workflow_collection=dependency_group.workflow_collection,
                workflow=dependency_step.workflow,
            )
        except ObjectDoesNotExist:
            raise ValidationError(
                "dependency_step's Workflow must be a "
                "member of the dependency_group's "
                "Workflow Collection"
            )
        else:
            dependency_step_workflow_order = dependency_step_workflow.order

        if dependency_step.workflow == dependency_group.workflow_step.workflow:
            # You cannot create a circular dependency.
            if dependency_step == dependency_group.workflow_step:
                raise ValidationError(
                    "The value of dependency_step cannot be equal to the "
                    "value of workflow_step in the associated dependency_"
                    "group. This would represent a circular dependency."
                )
            # The Dependency Step order cannot be later than the Workflow Step
            elif dependency_step.order > dependency_group.workflow_step.order:
                raise ValidationError(
                    "Dependency Step order cannot be later "
                    "than the Workflow Step order."
                )
        # Dependency Step Workflow Order cannot be later
        # than the Workflow Step Workflow order
        else:
            workflow_step_workflow_order = WorkflowCollectionMember.objects.get(
                workflow_collection=dependency_group.workflow_collection,
                workflow=dependency_group.workflow_step.workflow,
            ).order

            if dependency_step_workflow_order > workflow_step_workflow_order:
                raise ValidationError(
                    "Dependency Step Workflow Order "
                    "cannot be later than the Workflow "
                    "Step Workflow order."
                )


class WorkflowStepText(CreatedModifiedAbstractModel):
    """
    Text objects assigned to a WorkflowStep.

    A client is allowed to specify an arbitrary number
    of text elements to a given WorkflowStep. Just be aware
    that whenever you create a new UI template, you should know how
    many pieces of text that template will expect.

    Attributes:
        ui_identifier (CharField):
        content (CharField):
        storage_value (IntegerField):
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow_step = models.ForeignKey(WorkflowStep, on_delete=models.CASCADE)
    ui_identifier = models.CharField(
        max_length=200,
        help_text="Identifier used by user interface implementation to position the element on screen.",
    )
    content = models.CharField(max_length=500, help_text="The actual text.")
    storage_value = models.IntegerField(
        blank=True,
        null=True,
        help_text="The value that will be stored, in place of direct user input. This is used when multiple WorkflowStepText objects are used to represent single-choice options.",
    )

    class Meta:
        db_table = "workflow_system_step_text"
        unique_together = ["workflow_step", "ui_identifier"]
        verbose_name_plural = "Workflow Step Texts"

    def __str__(self):
        return self.ui_identifier


class WorkflowStepImage(CreatedModifiedAbstractModel):
    """
    Image objects assigned to a WorkflowStep.

    A client is allowed to specify an arbitrary number
    of images elements to a given WorkflowStep.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow_step = models.ForeignKey(WorkflowStep, on_delete=models.PROTECT)
    ui_identifier = models.CharField(
        max_length=200,
        help_text="Identifier used by user interface implementation to position the element on screen.",
    )
    url = models.ImageField(
        upload_to=workflow_step_media_folder,
        max_length=200,
        help_text="The image location.",
    )

    class Meta:
        db_table = "workflow_system_step_image"
        verbose_name_plural = "Workflow Step Images"
        unique_together = ["workflow_step", "ui_identifier"]

    def __str__(self):
        return self.ui_identifier


class WorkflowStepVideo(CreatedModifiedAbstractModel):
    """
    Video objects assigned to a WorkflowStep.

    A client is allowed to specify an arbitrary number
    of video elements to a given WorkflowStep.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow_step = models.ForeignKey(
        WorkflowStep,
        on_delete=models.PROTECT,
        help_text="The Workflow Step associated with the video.",
    )
    ui_identifier = models.CharField(
        max_length=200,
        help_text="Identifier used by user interface implementation to position the element on screen.",
    )
    url = models.URLField(help_text="Location of the video file.")

    class Meta:
        db_table = "workflow_system_step_video"
        verbose_name_plural = "Workflow Step Videos"
        unique_together = ["workflow_step", "ui_identifier"]

    def __str__(self):
        return self.ui_identifier


class WorkflowStepAudio(CreatedModifiedAbstractModel):
    """
    Audio objects assigned to a WorkflowStep.

    A client is allowed to specify an arbitrary number
    of audio elements to a given WorkflowStep.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow_step = models.ForeignKey(
        WorkflowStep,
        on_delete=models.PROTECT,
        help_text="The Workflow Step associated with the audio.",
    )
    ui_identifier = models.CharField(
        max_length=200,
        help_text="Identifier used by user interface implementation to position the element on screen.",
    )
    url = models.FileField(
        upload_to=workflow_step_media_folder,
        max_length=200,
        help_text="The location of the audio file.",
    )

    class Meta:
        db_table = "workflow_system_step_audio"
        verbose_name_plural = "Workflow Step Audio"
        unique_together = ["workflow_step", "ui_identifier"]

    def __str__(self):
        return self.ui_identifier


class WorkflowStepInput(CreatedModifiedAbstractModel):
    """
    Question objects assigned to a WorkflowStep.

    A client is allowed to specify an arbitrary number
    of question elements to a given WorkflowStep.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow_step = models.ForeignKey(
        WorkflowStep,
        on_delete=models.CASCADE,
        help_text="The WorkflowStep object that will own this object.",
    )
    ui_identifier = models.CharField(
        max_length=200,
        help_text="Identifier used by user interface implementation to position the element on screen.",
    )
    content = models.CharField(
        max_length=500, help_text="The actual text of the question."
    )
    required = models.BooleanField(
        help_text="Set to true if a response is required for this input."
    )
    response_schema = models.ForeignKey(
        JSONSchema,
        on_delete=models.PROTECT,
        help_text="A JSON Schema specification used to validate/reject user responses.",
    )

    class Meta:
        db_table = "workflow_system_step_input"
        unique_together = ["workflow_step", "ui_identifier"]
        verbose_name_plural = "Workflow Step Inputs"

    def __str__(self):
        return self.ui_identifier

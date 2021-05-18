"""Django model definition."""
import jsonschema
import uuid

from django.core.exceptions import ValidationError
from django.db import models

from jsonschema import Draft7Validator, SchemaError
from django_workflow_system.models.abstract_models import CreatedModifiedAbstractModel
from django_workflow_system.models.step import WorkflowStep


class WorkflowStepUserInputType(CreatedModifiedAbstractModel):
    """
    Question Type objects assigned to a WorkflowStep.

    Attributes:
        id (UUIDField): The unique UUID for the database record.
        name (CharField): The name of the question type.
        json_schema (JSONField): The schema that the specification must follow.
        placeholder_spec (JSONField): An example of properly formatted json that follows
                                      the json_schema.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150)
    json_schema = models.JSONField(help_text="Used to specify input, label, options, and correct answers.", verbose_name='JSON Schema')
    placeholder_specification = models.JSONField(help_text="Placeholder specification.")

    class Meta:
        db_table = "workflow_system_step_user_input_type"
        unique_together = ["name", "json_schema"]
        verbose_name_plural = "Workflow Step User Input Types"

    def __str__(self):
        return self.name

    def clean_fields(self, exclude=None):
        super(WorkflowStepUserInputType, self).clean_fields(exclude=exclude)

        try:
            Draft7Validator.check_schema(self.json_schema)
        except SchemaError as error:
            raise ValidationError(
                {
                    "json_schema": (
                        "There is something wrong in your json_schema definition. "
                        "Details {}".format(error)
                    )
                }
            )

        try:
            jsonschema.validate(instance=self.placeholder_specification, schema=self.json_schema)
        except jsonschema.ValidationError as error:
            raise ValidationError(
                {
                    "placeholder_specification": (
                        "There is something wrong in your placeholder_spec definition. "
                        "Details {}".format(error)
                    )
                }
            )


class WorkflowStepUserInput(CreatedModifiedAbstractModel):
    """
    Question objects assigned to a WorkflowStep.

    A WorkFlow author is allowed to specify an arbitrary number
    of question elements to a given WorkflowStep.

    Attributes:
        id (UUIDField): The unique UUID for the database record.
        workflow_step (ForeignKey): The WorkflowStep object that will own this object.
        ui_identifier (CharField): A simple string which is used to indicate
                                   to a user interface where to display this object
                                   within a template.
        required (BooleanField): True if a value is required for this input in the response JSON
        specification (JSONField): The specification of the WorkflowStepUserInput
        type (ForeignKey): The WorkflowStepUserInputType.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow_step = models.ForeignKey(WorkflowStep, on_delete=models.CASCADE)
    ui_identifier = models.CharField(max_length=200)
    required = models.BooleanField()
    specification = models.JSONField(help_text="Used to specify input, label, options, and correct answers.")
    type = models.ForeignKey(WorkflowStepUserInputType, on_delete=models.PROTECT)

    class Meta:
        db_table = "workflow_system_step_user_input"
        unique_together = ["workflow_step", "ui_identifier"]
        verbose_name_plural = "Workflow Step User Inputs"

    def __str__(self):
        return self.ui_identifier

    def clean_fields(self, exclude=None):
        super(WorkflowStepUserInput, self).clean_fields(exclude=exclude)

        try:
            jsonschema.validate(instance=self.specification, schema=self.type.json_schema)
        except jsonschema.ValidationError as error:
            raise ValidationError(
                {
                    "specification": (
                        "There is something wrong in your specification definition. "
                        "Details {}".format(error)
                    )
                }
            )

    @property
    def response_schema(self):
        """
        Returns the response schema for this given WorkflowStepUserInput.
        """
        try:
            correct_answer_schema = self.type.json_schema['properties']['correctAnswer']
            response_schema = {}
            for key, value in correct_answer_schema.items():
                if key in ['anyOf', 'type']:
                    response_schema[key] = value
                    if self.specification['requireCorrectAnswer']:
                        response_schema['enum'] = [self.specification['correctAnswer']]
                    else:
                        response_schema['enum'] = self.specification['options']
                    return response_schema
        except KeyError:
            # Not sure what we should do here.
            return {}
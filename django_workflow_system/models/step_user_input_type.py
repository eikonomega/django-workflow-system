"""Django model definition."""
import jsonschema
import uuid

from django.core.exceptions import ValidationError
from django.db import models

from jsonschema import Draft7Validator, SchemaError
from django_workflow_system.models.abstract_models import CreatedModifiedAbstractModel


class WorkflowStepUserInputType(CreatedModifiedAbstractModel):
    """
    Question Type objects assigned to a WorkflowStep.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="The unique UUID for the database record.",
    )
    name = models.CharField(
        max_length=150, help_text="The name of the question type.", unique=True
    )
    json_schema = models.JSONField(
        help_text="Used to specify input, label, options, and correct answers.",
        verbose_name="JSON Schema",
    )
    example_specification = models.JSONField(
        help_text="An example of properly formatted json that follows the json_schema."
    )

    class Meta:
        db_table = "workflow_system_step_user_input_type"
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
            jsonschema.validate(
                instance=self.example_specification, schema=self.json_schema
            )
        except jsonschema.ValidationError as error:
            raise ValidationError(
                {
                    "example_specification": (
                        "There is something wrong in your example_specification definition. "
                        "Details {}".format(error)
                    )
                }
            )

"""Django model definition."""

import uuid

from django.core.exceptions import ValidationError
from django.db import models

from jsonschema import Draft7Validator, SchemaError

from django_workflow_system.models.abstract_models import CreatedModifiedAbstractModel
from django_workflow_system.utils.validators import validate_code


class JSONSchema(CreatedModifiedAbstractModel):
    """
    JSON schemas are used to validate data coming into the system.

    In particular, when a WorkflowStep is defined, it is associated
    with a given schema. This is then used to validate the data
    provided by the user via API submission.

    This is a control to prevent bad data from getting into the system.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(
        max_length=100,
        help_text="A short-hand reference to the schema definition.",
        validators=[validate_code],
    )
    description = models.TextField(
        max_length=250,
        help_text="A human-friendly description of what is being defined in the JSONSchema.",
    )
    schema = models.JSONField()

    class Meta:
        db_table = "workflow_system_json_schema"
        verbose_name_plural = "JSON Schema Definitions (Advanced)"

    def __str__(self):
        return self.code

    def clean_fields(self, exclude=None):
        super(JSONSchema, self).clean_fields(exclude=exclude)

        try:
            Draft7Validator.check_schema(self.schema)
        except SchemaError as error:
            raise ValidationError(
                {
                    "schema": (
                        "There is something wrong in your schema definition. "
                        "Details {}".format(error)
                    )
                }
            )

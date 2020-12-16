"""
Model definitions related to Workflow JSON Schemas.
"""

import uuid

from django.core.exceptions import ValidationError
from django.db import models

from jsonschema import Draft7Validator, SchemaError

from workflows.models.abstract_models import CreatedModifiedAbstractModel


class JSONSchema(CreatedModifiedAbstractModel):
    """
    JSONSchema definitions for use within Workflows.

    Attributes:
        id (UUIDField): The unique UUID for the database record.
        code (CharField): A short-hand reference to the schema definition.
        description (TextField): A human-friendly description of what is being
                                 defined in the JSONSchema.
        schema (JSONField): A valid JSONSchema specification.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=100)
    description = models.TextField(max_length=250)
    schema = models.JSONField()

    class Meta:
        db_table = 'workflow_system_json_schema'
        verbose_name_plural = 'JSON Schema Definitions (Advanced)'

    def __str__(self):
        return self.code

    def clean_fields(self, exclude=None):
        super(JSONSchema, self).clean_fields(exclude=exclude)

        try:
            Draft7Validator.check_schema(self.schema)
        except SchemaError as error:
            raise ValidationError({
                'schema': (
                    'There is something wrong in your schema definition. '
                    'Details {}'.format(error))})

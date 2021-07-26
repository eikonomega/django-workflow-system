"""Django model definition."""
import importlib
import jsonschema
import os
from os import path
import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from django_workflow_system.models.abstract_models import CreatedModifiedAbstractModel
from django_workflow_system.models.step import WorkflowStep
from django_workflow_system.models.step_user_input_type import WorkflowStepUserInputType
from django_workflow_system.utils.response_schema_handlers import (
    date_range_question_schema,
    free_form_question_schema,
    multiple_choice_question_schema,
    numeric_range_question_schema,
    single_choice_question_schema,
    true_false_question_schema,
)


class WorkflowStepUserInput(CreatedModifiedAbstractModel):
    """
    Question objects assigned to a WorkflowStep.

    A WorkFlow author is allowed to specify an arbitrary number
    of question elements to a given WorkflowStep.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="The unique UUID for the database record.",
    )
    workflow_step = models.ForeignKey(
        WorkflowStep,
        on_delete=models.CASCADE,
        help_text="The WorkflowStep object that will own this object.",
    )
    ui_identifier = models.CharField(
        max_length=200,
        help_text="A simple string which is used to indicate to a user interface where to display this object within a template.",
    )
    required = models.BooleanField(
        help_text="True if a value is required for this input in the response JSON"
    )
    specification = models.JSONField(
        help_text="Used to specify input, label, options, and correct answers."
    )
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
            jsonschema.validate(
                instance=self.specification, schema=self.type.json_schema
            )
        except jsonschema.ValidationError as error:
            raise ValidationError(
                {
                    "specification": (
                        "There is something wrong in your specification definition. "
                        "Details {}".format(error.message)
                    )
                }
            )

        # Need to ensure that if correctInput is true, that inputRequired is also true.
        if (
            not self.specification["meta"]["inputRequired"]
            and self.specification["meta"]["correctInputRequired"]
        ):
            raise ValidationError(
                {
                    "specification": (
                        "There is something wrong in your specification definition. "
                        "Details: Inside `meta`, correctInputRequired can't be true if inputRequired is false"
                    )
                }
            )

    @property
    def response_schema(self):
        """
        Returns the response schema for this given WorkflowStepUserInput.
        """
        self._load_function_table()
        try:
            return self.__function_table[self.type.name](self)
        except KeyError:
            return {}

    __function_table = {
        "date_range_question": date_range_question_schema,
        "free_form_question": free_form_question_schema,
        "numeric_range_question": numeric_range_question_schema,
        "multiple_choice_question": multiple_choice_question_schema,
        "single_choice_question": single_choice_question_schema,
        "true_false_question": true_false_question_schema,
    }

    def _load_function_table(self):
        """Load all client created `get_response_schema` functions."""
        if hasattr(settings, "DJANGO_WORKFLOW_SYSTEM"):
            if (
                "INPUT_TYPE_RESPONSE_SCHEMA_HANDLERS"
                in settings.DJANGO_WORKFLOW_SYSTEM.keys()
            ):
                for directory in settings.DJANGO_WORKFLOW_SYSTEM[
                    "INPUT_TYPE_RESPONSE_SCHEMA_HANDLERS"
                ]:
                    try:
                        for file in os.listdir(path.join(directory)):
                            if "__init__" in file:
                                # Ignore the init file
                                continue
                            try:
                                # Create the module spec
                                module_spec = importlib.util.spec_from_file_location(
                                    file, f"{directory}/{file}"
                                )
                                # Create a new module  based  on the spec
                                module = importlib.util.module_from_spec(module_spec)
                                # An abstract method that executes the module
                                module_spec.loader.exec_module(module)
                                #  Get the actual function
                                real_func = getattr(module, "get_response_schema")
                                # Add it to our dictionary of functions
                                schema_handler = file.partition(".py")[0]
                                self.__function_table[schema_handler] = real_func
                            except (ModuleNotFoundError, AttributeError):
                                pass
                    except FileNotFoundError:
                        # the directory provided in the settings file does not exist
                        pass

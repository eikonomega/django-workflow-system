"""Django model definition."""
import uuid

from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db import models
from jsonschema import Draft7Validator, SchemaError

from django_workflow_system.models.collection_member import WorkflowCollectionMember
from django_workflow_system.models.step import WorkflowStep
from django_workflow_system.models.step_dependency_group import (
    WorkflowStepDependencyGroup,
)
from django_workflow_system.models.abstract_models import CreatedModifiedAbstractModel


class WorkflowStepDependencyDetail(CreatedModifiedAbstractModel):
    """
    This model represents a single dependency specification
    within a dependency group.

    Attributes:
        id (UUIDField): The unique UUID for the database record.
        dependency_group (ForeignKey): The Dependency Group the Step Dependency belongs to.
        dependency_step (ForeignKey): The WorkflowStep object that is being depended on.
        required_response (JSONField): The user response that is required for the dependency to be
                                       considered fulfilled.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dependency_group = models.ForeignKey(
        WorkflowStepDependencyGroup, on_delete=models.CASCADE
    )
    dependency_step = models.ForeignKey(WorkflowStep, on_delete=models.CASCADE)
    required_response = models.JSONField()

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

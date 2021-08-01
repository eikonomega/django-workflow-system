"""Django model definition."""
import uuid

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import models

from django_workflow_system.models.collection_member import WorkflowCollectionMember
from django_workflow_system.models.collection import WorkflowCollection
from django_workflow_system.models.abstract_models import CreatedModifiedAbstractModel


class WorkflowStepDependencyGroup(CreatedModifiedAbstractModel):
    """
    This model allows multiple step dependencies to be grouped together as a
    logical set of dependencies.

    Attributes:
        id (UUIDField): The unique UUID for the database record.
        workflow_collection (ForeignKey): The Workflow Collection of the Step's Workflow
        workflow_step (ForeignKey): The WorkflowStep object that will have a dependency.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow_collection = models.ForeignKey(
        WorkflowCollection, on_delete=models.CASCADE
    )
    workflow_step = models.ForeignKey("WorkflowStep", on_delete=models.CASCADE)

    class Meta:
        db_table = "workflow_system_step_dependency_group"
        verbose_name_plural = "Workflow Step Dependency Groups"

    def __str__(self):
        return "{} - {}".format(self.workflow_step.code, self.workflow_collection.code)

    def clean(self):
        """
        Provide custom validation for the following:
        * Step's workflow must be a member of the Workflow Collection
        """
        try:
            WorkflowCollectionMember.objects.get(
                workflow_collection=self.workflow_collection,
                workflow=self.workflow_step.workflow,
            )
        except ObjectDoesNotExist:
            raise ValidationError(
                "Step's workflow must be a member of the Workflow Collection."
            )

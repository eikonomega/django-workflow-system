"""Django model definition."""
import uuid

from django.db import models
from django.conf import settings
from django.utils import timezone

from .abstract_models import CreatedModifiedAbstractModel
from .collection import WorkflowCollection


class WorkflowCollectionRecommendation(CreatedModifiedAbstractModel):
    """
    Definition of a Workflow Recommendation.

    Assignments
    -----------
    id : uuid
        The unique UUID of the record.
    workflow_collection : foreign key
        The WorkflowCollection object associated with the Assignment.
    user : foreign key
        The User being assigned the Workflow.
    start: datetime
        The start date for which the recommendation is valid.
        Defaults to now.
    end : datetime
        The end date for which the recommendation is valid.
        Defaults to null, which represents infinity.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow_collection = models.ForeignKey(
        WorkflowCollection, on_delete=models.CASCADE
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    start = models.DateTimeField(default=timezone.now)
    end = models.DateTimeField(null=True, blank=True, default=None)

    class Meta:
        db_table = "workflow_system_collection_recommendation"
        verbose_name_plural = "Workflow Collection Recommendations"

    def __str__(self):
        return " - ".join([str(self.workflow_collection), str(self.user)])

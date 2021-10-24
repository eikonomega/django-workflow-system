"""Django model definition."""
import uuid

from django.db import models
from django.utils import timezone

from django_workflow_system.models.abstract_models import CreatedModifiedAbstractModel
from django_workflow_system.models.step import WorkflowStep


class WorkflowCollectionEngagementDetail(CreatedModifiedAbstractModel):
    """
    Used to record user engagement with individual steps of a Workflow.

    Note: an incomplete WorkflowCollectionEngagementDetail
    that is not finished DOES NOT EXIST except for the purpose
    of filling in fields when a user navigates again to a step
    which they had previously left incomplete. Most queries on
    WorkflowCollectionEngagementDetails should exclude instances
    where finished=None.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="The unique UUID of the record.",
    )
    workflow_collection_engagement = models.ForeignKey(
        "WorkflowCollectionEngagement",
        on_delete=models.PROTECT,
        help_text="The WorkflowCollectionEngagement object associated with the engagement detail.",
    )
    step = models.ForeignKey(
        WorkflowStep,
        on_delete=models.PROTECT,
        help_text="The WorkflowStep associated with the engagement detail.",
    )
    user_responses = models.JSONField(
        null=True,
        blank=True,
        help_text="Internal representation of JSON response from user.",
    )
    started = models.DateTimeField(
        default=timezone.now, help_text="The start date of the engagement detail."
    )
    finished = models.DateTimeField(
        blank=True, null=True, help_text="The finish date of the engagement detail."
    )

    class Meta:
        db_table = "workflow_system_collection_engagement_detail"
        verbose_name_plural = "Workflow Collection Engagement Details"
        unique_together = ["workflow_collection_engagement", "step"]
        ordering = ["workflow_collection_engagement", "started"]

    def __str__(self):
        return "{} response to {}".format(
            self.workflow_collection_engagement.user.username,
            self.workflow_collection_engagement.workflow_collection.name,
        )

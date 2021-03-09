"""Django model definition."""
import uuid

from django.db import models
from django.utils import timezone

from workflows.models.abstract_models import CreatedModifiedAbstractModel
from workflows.models.step import WorkflowStep


class WorkflowCollectionEngagementDetail(CreatedModifiedAbstractModel):
    """
    Used to record user engagement with individual steps of a Workflow.

    Note: an incomplete WorkflowCollectionEngagementDetail
    that is not finished DOES NOT EXIST except for the purpose
    of filling in fields when a user navigates again to a step
    which they had previously left incomplete. Most queries on
    WorkflowCollectionEngagementDetails should exclude instances
    where finished=None.

    Attributes:
        id (UUIDField): The unique UUID of the record.
        workflow_collection_engagement (ForeignKey): The WorkflowCollectionEngagement object
                                                     associated with the engagement detail.
        step (ForeignKey): The WorkflowStep associated with the engagement detail.
        user_response (JSONField): Internal representation of JSON response from user.
                                   If present, user_response is expected to be of the following form:
                               {
                                   "questions": [
                                       {
                                           "stepInputID": <uuid>,
                                           "stepInputUIIdentifier": "string",
                                           "response": <JSON>
                                        },
                                        {
                                           "stepInputID": <uuid>,
                                           "stepInputUIIdentifier": "string",
                                           "response": <JSON>
                                        }
                                    ]
                                }
        started (DateTimeField): The start date of the engagement detail.
        finished (DateTimeField): The finish date of the engagement detail.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow_collection_engagement = models.ForeignKey(
        "WorkflowCollectionEngagement", on_delete=models.PROTECT
    )
    step = models.ForeignKey(WorkflowStep, on_delete=models.PROTECT)
    user_response = models.JSONField(null=True, blank=True)
    started = models.DateTimeField(default=timezone.now)
    finished = models.DateTimeField(blank=True, null=True)

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
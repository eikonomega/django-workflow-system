"""Django model definition."""
from typing import TypedDict, List, Union
import uuid

import jsonschema
from django.conf import settings
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db import models
from django.db.models import Subquery, OuterRef, Q
from django.utils import timezone

from django_workflow_system.models.abstract_models import CreatedModifiedAbstractModel
from django_workflow_system.models.collection_member import WorkflowCollectionMember
from django_workflow_system.models.step import WorkflowStep
from django_workflow_system.models.step_dependency_group import (
    WorkflowStepDependencyGroup,
)

from django_workflow_system.models.collection import WorkflowCollection
from django_workflow_system.models.engagement_detail import (
    WorkflowCollectionEngagementDetail,
)


class EngagementStateType(TypedDict):
    """Type definition for the state of an engagement."""

    next_workflow_id: Union[str, None]
    next_step_id: Union[str, None]
    prev_step_id: Union[str, None]
    prev_workflow_id: Union[str, None]
    steps_completed_in_collection: int
    steps_in_collection: int
    steps_completed_in_workflow: int
    steps_in_workflow: int
    previously_completed_workflows: List[str]


class WorkflowCollectionEngagement(CreatedModifiedAbstractModel):
    """
    Used to track user engagement with a Workflow Collection.

    When a user interacts with a workflow collection, we call that an engagement.
    It is also functionally the container of `WorkflowCollectionEngagementDetail`
    objects.

    Of special importance is the `state` property of this class,
    which is used to identify where the user is during a given
    engagement in relationship to the whole collection.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow_collection = models.ForeignKey(
        WorkflowCollection, on_delete=models.PROTECT
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    started = models.DateTimeField(default=timezone.now)
    finished = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "workflow_system_collection_engagement"
        unique_together = ["workflow_collection", "user", "started"]
        verbose_name_plural = "Workflow Collection Engagements"
        ordering = ["workflow_collection", "started"]

    @property
    def state(self) -> EngagementStateType:
        """
        Determine the user's current state in relationship to the whole collection.

        Practically speaking, what workflows and steps have been completed thus far,
        and which ones still need to be completed.

        Returns:
            dict: Containing the Workflow UUID, WorkflowStep UUID and
                  a list of previously_completed_workflows that
                  are needed by client UI's to present the correct
                  Workflow step to the user.
        """

        prev_step: WorkflowStep = None
        next_step: WorkflowStep = None

        # take every step
        # filter by steps which belong to workflows which are members of this workflow collection
        # annotate each step with its workflow's order in the workflow collection
        # order by workflow order first, then order within the workflow

        step_to_member = WorkflowCollectionMember.objects.filter(
            workflow_collection=self.workflow_collection, workflow=OuterRef("workflow")
        )

        step_list = (
            WorkflowStep.objects.filter(
                workflow__workflowcollectionmember__workflow_collection=self.workflow_collection
            )
            .annotate(wf_order=Subquery(step_to_member.values("order")[:1]))
            .order_by("wf_order", "order")
        )

        if not step_list:
            return {
                "next_workflow_id": None,
                "next_step_id": None,
                "prev_step_id": None,
                "prev_workflow_id": None,
                "steps_completed_in_collection": 0,
                "steps_in_collection": 0,
                "steps_completed_in_workflow": 0,
                "steps_in_workflow": 0,
                "previously_completed_workflows": [],
            }

        ######## Calculating Previous Step ########
        for idx_prev_step, step in reversed(list(enumerate(step_list))):
            if WorkflowCollectionEngagementDetail.objects.filter(
                workflow_collection_engagement=self,
                finished__isnull=False,  # step has been finished
                step=step,
            ):
                prev_step = step
                break

        ######## Calculating Next Step ########
        if self.workflow_collection.category == "ACTIVITY":
            if not prev_step:
                if self.workflowcollectionengagementdetail_set.all():
                    # if we can figure out what workflow we're in, return the first step in that workflow
                    workflow = self.workflowcollectionengagementdetail_set.all()[
                        0
                    ].step.workflow
                    next_step = workflow.workflowstep_set.order_by("order").first()
                else:
                    next_step = step_list[0]
            elif idx_prev_step + 1 >= len(step_list):
                next_step = None
            else:
                next_step = step_list[idx_prev_step + 1]
        elif self.workflow_collection.category == "SURVEY":
            if not prev_step:
                next_step = step_list[0]
            else:
                for step in step_list[idx_prev_step + 1 :]:
                    # step hasn't been started, check if can begin
                    if self.all_dependencies_satisfied(step):
                        next_step = step
                        break

        ######## Calculating Percent Completion ########

        if next_step:
            wf_order = self.workflow_collection.workflowcollectionmember_set.get(
                workflow__workflowstep=next_step
            ).order
            steps_completed_in_collection = step_list.filter(
                Q(wf_order__lt=wf_order)
                | Q(wf_order=wf_order, order__lt=next_step.order)
            ).count()
            steps_in_collection = step_list.count()

            steps_completed_in_workflow = next_step.workflow.workflowstep_set.filter(
                order__lt=next_step.order
            ).count()
            steps_in_workflow = next_step.workflow.workflowstep_set.count()
        else:
            steps_completed_in_collection = step_list.count()
            steps_in_collection = step_list.count()

            steps_completed_in_workflow = prev_step.workflow.workflowstep_set.count()
            steps_in_workflow = prev_step.workflow.workflowstep_set.count()

        ######## Calculating Previously Completed Workflows ########
        collection_members = (
            self.workflow_collection.workflowcollectionmember_set.all().order_by(
                "order"
            )
        )
        completed_workflows_list = (
            []
        )  # workflows a user has completed that may be taken again.

        if self.workflow_collection.category == "ACTIVITY":
            for member in collection_members:
                # Check that the user has completed all steps for the
                # Workflow at some point in some engagement
                workflow_steps = member.workflow.workflowstep_set.all()
                completed_all_steps = True  # true until we find an incomplete step
                for step in workflow_steps:
                    # if there is not a finished engagement detail for this step, then the step and member are incomplete
                    if not WorkflowCollectionEngagementDetail.objects.filter(
                        workflow_collection_engagement__user=self.user,
                        # this part is different between the two loops
                        step=step,
                        finished__isnull=False,
                    ):
                        completed_all_steps = False
                        break
                if completed_all_steps:
                    completed_workflows_list.append({"workflow_id": member.workflow.id})
        elif self.workflow_collection.category == "SURVEY":
            if next_step is not None:
                # if there exists a next_step, then then that step's workflow and the workflows after it are unfinished
                unfinished_member = (
                    self.workflow_collection.workflowcollectionmember_set.get(
                        workflow=next_step.workflow
                    )
                )
                # the finished workflows are all the workflows with order before the unfinished workflow
                collection_members = collection_members.filter(
                    order__lt=unfinished_member.order
                )
            for member in collection_members:
                completed_workflows_list.append({"workflow_id": member.workflow.id})

        return {
            "next_workflow_id": next_step.workflow.id if next_step else None,
            "next_step_id": next_step.id if next_step else None,
            "prev_step_id": prev_step.id if prev_step else None,
            "prev_workflow_id": prev_step.workflow.id if prev_step else None,
            "steps_completed_in_collection": steps_completed_in_collection,
            "steps_in_collection": steps_in_collection,
            "steps_completed_in_workflow": steps_completed_in_workflow,
            "steps_in_workflow": steps_in_workflow,
            "previously_completed_workflows": completed_workflows_list,
        }

    def all_dependencies_satisfied(self, step):
        step_dependency_group_list = WorkflowStepDependencyGroup.objects.filter(
            workflow_collection=self.workflow_collection,
            workflow_step=step,
        )
        if len(step_dependency_group_list) == 0:
            return True
        for step_dependency_group in step_dependency_group_list:
            dependency_group_satisfied = True
            for (
                dependency_detail
            ) in step_dependency_group.workflowstepdependencydetail_set.all():
                required_step = dependency_detail.dependency_step
                required_response_schema = dependency_detail.required_response
                try:
                    required_step_response = (
                        self.workflowcollectionengagementdetail_set.get(
                            step=required_step,
                            finished__isnull=False,
                        ).user_responses
                    )
                except WorkflowCollectionEngagementDetail.DoesNotExist as e:
                    dependency_group_satisfied = False
                    break
                questions_list = required_step_response[-1]["inputs"]
                try:
                    jsonschema.validate(
                        instance=questions_list, schema=required_response_schema
                    )
                except jsonschema.ValidationError as e:
                    dependency_group_satisfied = False
                    break
            if dependency_group_satisfied:
                return True
        # no dependency_group was completely satisfied
        return False

    def __str__(self):
        return "Engagement: {} - {}".format(
            self.workflow_collection.name, self.user.username
        )

    def clean(self, *args, **kwargs):
        # User must be active to engage in a collection
        if not self.user.is_active:
            raise ValidationError(
                {"user": "User must be active to engage in a collection."}
            )

        # If this engagement's collection has an unassigned assignment associated with it then
        try:
            assignment = self.workflow_collection.workflowcollectionassignment_set.get(
                engagement=None, status="ASSIGNED"
            )
            assignment.engagement = self
            assignment.save()
        except ObjectDoesNotExist:
            pass

        # Ensure finish date is later than start date
        if self.finished is not None:
            if self.finished < self.started:
                raise ValidationError(
                    "The finish date must be later than the start date."
                )
            if self.workflow_collection.category == "SURVEY":
                if self.state[
                    "next_step_id"
                ]:  # i.e. there is still a next step which can be completed
                    raise ValidationError(
                        "There are still steps which can be completed"
                    )

        if hasattr(self, "workflowcollectionassignment"):
            if (
                self.workflow_collection
                != self.workflowcollectionassignment.workflow_collection
            ):
                raise ValidationError(
                    "The Engagement and Assignment "
                    "WorkflowCollections are not the same"
                )
            elif self.user != self.workflowcollectionassignment.user:
                raise ValidationError(
                    "The Engagement and Assignment Users are not the same"
                )
        # Check if the user has an existing incomplete engagement to the same workflow collection
        existing_engagement = WorkflowCollectionEngagement.objects.filter(
            user=self.user,
            workflow_collection=self.workflow_collection,
            finished__isnull=True,
        ).exclude(pk=self.pk)
        if existing_engagement:
            raise ValidationError(
                "The user has an existing incomplete engagement for this workflow collection."
            )

        if self.finished is not None:
            # Clean the finished engagement by deleting unfinished details
            self.workflowcollectionengagementdetail_set.filter(finished=None).delete()

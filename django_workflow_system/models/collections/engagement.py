"""Django model definition."""
from typing import TypedDict, List, Union
import uuid
from django.db.models.expressions import F, Window
from django.db.models.functions import RowNumber
from django.db.models.query import QuerySet

import jsonschema
from django.conf import settings
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db import models
from django.db.models import Subquery, OuterRef, Q
from django.utils import timezone

from django_workflow_system.models.abstract_models import CreatedModifiedAbstractModel
from django_workflow_system.models.collections.collection_member import (
    WorkflowCollectionMember,
)
from django_workflow_system.models.step import WorkflowStep
from django_workflow_system.models.step_dependency_group import (
    WorkflowStepDependencyGroup,
)

from django_workflow_system.models.collections.collection import WorkflowCollection
from django_workflow_system.models.collections.engagement_detail import (
    WorkflowCollectionEngagementDetail,
)
from django_workflow_system.models.workflow import Workflow


class PreviousNextStepDescriptor(TypedDict):
    step_id: Union[str, None]
    workflow_id: Union[str, None]


class PreviouslyCompletedWorkflows(TypedDict):
    current_engagement: List[str]
    any_engagement: List[str]


class EngagementStateSummary(TypedDict):
    steps_completed_in_collection: int
    steps_in_collection: int
    steps_completed_in_workflow: int
    steps_in_workflow: int
    previously_completed_workflows: PreviouslyCompletedWorkflows


class EngagementStateType(TypedDict):
    """Type definition for the state of an engagement."""

    previous: PreviousNextStepDescriptor
    next: PreviousNextStepDescriptor
    summary: EngagementStateSummary


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
        WorkflowCollection,
        on_delete=models.PROTECT,
        help_text="The collection which the engagement records data for.",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        help_text="The user to whom the engagement belongs.",
    )
    started = models.DateTimeField(
        default=timezone.now, help_text="When the user started the engagment."
    )
    finished = models.DateTimeField(
        blank=True, null=True, help_text="When the user finished the engagement."
    )

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
        """

        """
        STEP 1
        Get all steps associated with the collection. Annotate so that you 
        have both the order of the step in each workflow and also the order of
        the workflow the step is a part of in the collection.

        This is necessary because you need both pieces of information to really
        order the steps correctly.
        """
        all_collection_steps: QuerySet[WorkflowStep] = (
            WorkflowStep.objects.filter(
                workflow__workflowcollectionmember__workflow_collection=self.workflow_collection
            )
            .annotate(workflow_order=F("workflow__workflowcollectionmember__order"))
            .order_by("workflow_order", "order")
        )

        for step in all_collection_steps:
            print(step.__dict__)

        # Special case to prevent crash when collection has no steps.
        if not all_collection_steps:
            return {
                "next": {"step_id": None, "workflow_id": None},
                "previous": {"step_id": None, "workflow_id": None},
                "summary": {
                    "steps_completed_in_collection": None,
                    "steps_in_collection": None,
                    "steps_completed_in_workflow": None,
                    "steps_in_workflow": None,
                    "previously_completed_workflows": {
                        "any_engagement": [],
                        "current_engagement": [],
                    },
                },
            }

        """
        STEP 2
        Collect data we will use at various points.
        """
        all_collection_workflows: QuerySet[Workflow] = (
            Workflow.objects.filter(
                workflowcollectionmember__workflow_collection=self.workflow_collection
            )
            .annotate(workflow_order=F("workflowcollectionmember__order"))
            .order_by("workflowcollectionmember__order")
        )

        all_engagement_details: QuerySet[
            WorkflowCollectionEngagementDetail
        ] = self.workflowcollectionengagementdetail_set.all()
        all_completed_engagement_details = all_engagement_details.filter(
            finished__isnull=False
        )

        """
        STEP 3: Determine if there is a previous step.
        """
        previousDescriptor: PreviousNextStepDescriptor
        previous_step: WorkflowStep
        previous_workflow: Workflow

        if not all_completed_engagement_details:
            # If there are no completed engagement details, this means that
            # the engagement is brand new and there is no previous step.
            previous_step = None
            previous_workflow = None
        else:
            """
            If there are engagement details, then we have 2 possibilities to
            consider.

            The first is that the user is in the middle of a workflow -
            in which case there will a previous step.

            The second is when the user has completed one of the workflows and is
            more complicated depended on the characteristics of the collection.
            """
            if (
                self.workflow_collection.category == "SURVEY"
                or self.workflow_collection.ordered
            ):
                # Since these types of collections require steps to be completed in order,
                # just find the last completed step and mark that are the previous step.
                for step in reversed(list(all_collection_steps)):
                    try:
                        all_completed_engagement_details.get(step=step)
                        previous_step = step
                        previous_workflow = step.workflow
                    except WorkflowCollectionEngagementDetail.DoesNotExist:
                        continue
                    else:
                        break

            else:
                """
                Here is the complicated one. When we are dealing with an unordered activity,
                workflows do not need to be completed in order, which means there
                is no definitive and predicatable ordering of steps.

                That said, there is an enforcement at the serializer level that will prevent
                a user from skipping between workflows until all the steps of a workflow
                are finished. In other words, users can do workflows out of order, but
                once they start a workflow, they have to finish it before switching
                to another workflow.

                We can take advantage of this.
                """
                for workflow in all_collection_workflows:
                    # Grab any completed steps for the current loop iteration's workflow.
                    unfinished_engagement_detail = (
                        all_completed_engagement_details.filter(
                            step__workflow=workflow
                        ).order_by("step__order")
                    )

                    # Determine if the user is currently "in-progress" on this workflow.
                    # This means there is at least one completed step in the workflow.
                    if (
                        unfinished_engagement_detail.count()
                        and unfinished_engagement_detail.count()
                        < workflow.workflowstep_set.count()
                    ):
                        # If so, the previous step is the last complete step.
                        previous_step = all_collection_steps.get(
                            id=unfinished_engagement_detail.last().step.id
                        )
                        previous_workflow = previous_step.workflow
                        break
                else:
                    previous_step = None
                    previous_workflow = None

        previousDescriptor = {
            "step_id": previous_step.id if previous_step else None,
            "workflow_id": previous_workflow.id if previous_step else None,
        }

        """
        STEP 4: Determine if there is a next step.
        """
        nextDescriptor: PreviousNextStepDescriptor
        next_step: WorkflowStep
        next_workflow: Workflow

        # If there are no completed steps/engagement details, the
        # first step of the collection should be used.
        if not all_completed_engagement_details:
            next_step = all_collection_steps[0]
            next_workflow = next_step.workflow

        if previous_step:

            # See if there are any steps remaining in the workflow.
            next_step_in_workflow = (
                all_collection_steps.filter(
                    workflow=previous_step.workflow, order__gt=previous_step.order
                )
                .order_by("order")
                .first()
            )

            if next_step_in_workflow:
                next_step = next_step_in_workflow
                next_workflow = next_step_in_workflow.workflow

            elif (
                self.workflow_collection.category == "SURVEY"
                or self.workflow_collection.ordered
            ):
                """
                If there isn't another step in the workflow AND the collection is a survey
                or an ordered activity, we can use the first step of the next workflow in the
                collection (if there is one) as the next step.

                TODO: Need to re-introduce dependency checking here.
                In light of that... need to account for the possibility
                that you may need to skip over multiple workflows before you
                find a step for which all dependencies are meet.

                Go through steps in index order sort of like Rocky had previously.
                """
                first_step_of_next_workflow = (
                    all_collection_steps.filter(
                        workflow_order__gt=previous_step.workflow_order
                    )
                    .order_by("order")
                    .first()
                )

                if first_step_of_next_workflow:
                    next_step = first_step_of_next_workflow
                    next_workflow = first_step_of_next_workflow.workflow
                else:
                    # The user has completed all steps in the collection.
                    # They are done. :)
                    next_step = None
                    next_workflow = None

        elif (
            self.workflow_collection.category == "ACTIVITY"
            and not self.workflow_collection.ordered
        ):
            """
            If there is no previous step for an unordered activity, this can mean
            one of two things.

            The first is the engagement is brand new in which case the
            next step should be set to the first step of the collection.
            This case has already been handled previously.

            The second is when a workflow has been started (i.e. there is
            a single unfinished engagement detail) that is not the first
            workflow of the collection.
            """
            print("UNORDERED ACTIVITY")

            next_step = None
            next_workflow = None

            for workflow in all_collection_workflows:
                # See if there is an unfinished engagement detail
                try:
                    unfinished_engagement_detail = all_engagement_details.get(
                        step__workflow=workflow, finished__isnull=True
                    )
                except WorkflowCollectionEngagementDetail.DoesNotExist:
                    pass
                else:
                    next_step = all_collection_steps.get(
                        id=unfinished_engagement_detail.step.id
                    )
                    next_workflow = next_step.workflow
                    break

        nextDescriptor = {
            "step_id": next_step.id if next_step else None,
            "workflow_id": next_workflow.id if next_step else None,
        }

        """
        STEP 5: Determine how much progress the user has made in the current engagement.
        """

        # How many steps are in the collection?
        steps_in_collection_count = all_collection_steps.count()

        # How many steps are completed in this engagement for the collection?
        completed_steps_in_collection_count = 0

        for step in all_collection_steps:
            try:
                all_completed_engagement_details.get(step=step)
            except WorkflowCollectionEngagementDetail.DoesNotExist:
                pass
            else:
                completed_steps_in_collection_count += 1

        """
        Now we will determine how many steps are left to complete in the current workflow.
        This gets a little tricky as you have to answer the question 'what determines the current collection`?

        For our purposes, we will take the workflow of `next_step` to be the current collection.
        """

        if next_step:
            steps_in_workflow = next_step.workflow.workflowstep_set.all()
            steps_in_workflow_count = steps_in_workflow.count()
            completed_steps_in_workflow_count = 0

            for step in steps_in_workflow:
                try:
                    all_completed_engagement_details.get(step=step)
                except WorkflowCollectionEngagementDetail.DoesNotExist:
                    pass
                else:
                    completed_steps_in_workflow_count += 1
        else:
            # There is no currently in progress workflow.
            steps_in_workflow_count = None
            completed_steps_in_workflow_count = None

        """
        STEP 6: Calculating Previously Completed Workflows

        Determine which workflows have been completed. Either in this engagement
        or in a previous engagement.
        """
        completed_workflows_in_this_engagement = []
        completed_workflows_in_any_engagement = []

        for workflow in all_collection_workflows:
            workflow_steps = workflow.workflowstep_set.all()

            # We will mark these as false as needed.
            completed_in_this_engagement = True
            completed_in_any_engagement = True

            for step in workflow_steps:
                previous_step_completions = (
                    WorkflowCollectionEngagementDetail.objects.filter(
                        workflow_collection_engagement__user=self.user,
                        step=step,
                        finished__isnull=False,
                    )
                )

                if not previous_step_completions.filter(
                    workflow_collection_engagement=self
                ):
                    completed_in_this_engagement = False

                if not previous_step_completions:
                    completed_in_any_engagement = False
                    # No need to process further steps since we know this step
                    # wasn't completed in any engagement.
                    break

            if completed_in_any_engagement:
                completed_workflows_in_any_engagement.append(workflow.id)
            if completed_in_this_engagement:
                completed_workflows_in_this_engagement.append(workflow.id)

        return {
            "next": nextDescriptor,
            "previous": previousDescriptor,
            "summary": {
                "steps_completed_in_collection": completed_steps_in_collection_count,
                "steps_in_collection": steps_in_collection_count,
                "steps_completed_in_workflow": completed_steps_in_workflow_count,
                "steps_in_workflow": steps_in_workflow_count,
                "previously_completed_workflows": {
                    "any_engagement": completed_workflows_in_any_engagement,
                    "current_engagement": completed_workflows_in_this_engagement,
                },
            },
        }

    # TODO: Put this back in place.
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

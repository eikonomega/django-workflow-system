import logging
from datetime import timedelta

from django.core.management import BaseCommand
from django.db.models import Q
from django.utils import timezone

from website.utils.logging_utils import generate_extra
from website.workflows.models import (
    WorkflowCollectionAssignment,
    WorkflowCollectionEngagement,
)

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """This command closes complete assignments, and incomplete assignments after 30 days"""

    excluded_workflow_collections = ("demographics_survey_welcome_collection",)

    def handle(self, *args, **options):
        """
        This command has three jobs related to Survey Workflow Collection Assignments.

        First, it takes every assignment which is in progress but has a finished
        engagement, and marks it as closed complete

        Next it takes every Assignment 30 days old which is not complete, and not in
        the list of excluded workflow collections, and marks it as closed-incomplete

        Finally, this adds an end date for workflow collection engagements which are from
        assignments which have been closed incomplete
        """
        print("Starting Assignment Terminator. Hasta la vista, Baby!", file=self.stdout)

        # mark any in-progress survey assignments with finished engagements as complete
        assignments_marked_complete = WorkflowCollectionAssignment.objects.filter(
            workflow_collection__category="SURVEY",
            status=WorkflowCollectionAssignment.IN_PROGRESS,
            engagement__finished__isnull=False,
        )
        
        for assignment in assignments_marked_complete:
            logger.info(
                "Assignment terminator marked assigment of collection %s to user %s as CLOSED_COMPLETE",
                assignment.workflow_collection.code,
                assignment.user,
                extra=generate_extra(
                    event_code="WORKFLOW_COLLECTION_ASSIGNMENT_COMPLETED",
                    workflow_collection_assignment=assignment
                ),
            )
        assignments_marked_complete_count = assignments_marked_complete.update(
            status=WorkflowCollectionAssignment.CLOSED_COMPLETE
        )

        # takes all assignments which are...
        #   * surveys
        #   * old
        #   * not complete
        #   * not excluded
        # ... and marks them as incomplete
        assignments_marked_incomplete = WorkflowCollectionAssignment.objects.filter(
            workflow_collection__category="SURVEY",
            assigned_on__lte=timezone.now() - timedelta(days=30),
        ).exclude(
            status__in=(
                WorkflowCollectionAssignment.CLOSED_COMPLETE,
                WorkflowCollectionAssignment.CLOSED_INCOMPLETE,
            )
        ).exclude(
            workflow_collection__code__in=self.excluded_workflow_collections
        )
        for assignment in assignments_marked_incomplete:
            logger.info(
                "Assignment terminator marked assigment of collection %s to user %s as CLOSED_INCOMPLETE",
                assignment.workflow_collection.code,
                assignment.user,
                extra=generate_extra(
                    event_code="WORKFLOW_COLLECTION_ASSIGNMENT_MARKED_INCOMPLETE",
                    workflow_collection_assignment=assignment
                ),
            )
        assignments_marked_incomplete_count = assignments_marked_incomplete.update(
            status=WorkflowCollectionAssignment.CLOSED_INCOMPLETE
        )

        # mark any engagements for closed incomplete assignments as finished
        engagements_marked_finished = WorkflowCollectionEngagement.objects.filter(
            finished__isnull=True,
            workflowcollectionassignment__status=WorkflowCollectionAssignment.CLOSED_INCOMPLETE,
        )
        for engagement in engagements_marked_finished:
            logger.info(
                "Assignment terminator marked engagement of collection %s to user %s as finished",
                engagement.workflow_collection.code,
                engagement.user,
                extra=generate_extra(
                    event_code="WORKFLOW_COLLECTION_ENGAGEMENT_MARKED_COMPLETE",
                    workflow_collection_engagement=engagement,
                ),
            )
        engagements_marked_finished_count = engagements_marked_finished.update(
            finished=timezone.now(),
        )

        print("Finished Assignment Terminator.", file=self.stdout)
        print(
            f"{assignments_marked_incomplete_count} WorkflowCollectionAssignments changed to CLOSED_INCOMPLETE.",
            file=self.stdout,
        )
        print(
            f"{assignments_marked_complete_count} WorkflowCollectionAssignments changed to CLOSED_COMPLETE.",
            file=self.stdout,
        )
        print("I'll be back...", file=self.stdout)
        logger.info(
            "Finished assignment terminator: complete/incomplete %d/%d",
            assignments_marked_complete_count,
            assignments_marked_incomplete_count,
            extra={
                "event_code": "ASSIGNMENT_TERMINATOR",
                "assignments_marked_complete_count": assignments_marked_complete_count,
                "assignments_marked_incomplete_count": assignments_marked_incomplete_count,
                "engagements_marked_finished_count": engagements_marked_finished_count,
            },
        )

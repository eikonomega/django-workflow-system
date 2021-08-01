# from datetime import timedelta
#
# from django.core.management import call_command
# from django.test import TestCase
# from django.utils import timezone
# from io import StringIO
#
# from ....api.tests.factories import (
#     WorkflowCollectionAssignmentFactory,
#     WorkflowCollectionAssignment2Factory, UserFactory)
# from ....models import (WorkflowCollectionEngagement,
#                         WorkflowCollectionAssignment)
#
# from ....api.tests.factories.workflows.workflow_collection import (
#     WorkflowCollectionFactory, WorkflowCollection2Factory)
#
# import django_workflow_system.api.tests.factories as factories
#
#
from io import StringIO
from datetime import timedelta

from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from django_workflow_system.api.tests.factories import (
    WorkflowCollectionFactory,
    WorkflowCollectionAssignmentFactory,
    UserFactory,
    WorkflowCollectionEngagementFactory,
)
from django_workflow_system.models import (
    WorkflowCollectionEngagement,
    WorkflowCollectionAssignment,
)


class TestCommand(TestCase):
    def setUp(self):
        self.workflow_collection = WorkflowCollectionFactory(category="SURVEY")
        self.workflow_collection2 = WorkflowCollectionFactory(category="SURVEY")
        self.user = UserFactory()

        # Engagement + Assignment that gets closed
        self.workflow_collection_engagement_1 = (
            WorkflowCollectionEngagement.objects.create(
                workflow_collection=self.workflow_collection,
                user=self.workflow_collection.created_by,
                started=timezone.now() - timedelta(days=42),
            )
        )
        self.assignment_1 = WorkflowCollectionAssignmentFactory(
            user=self.workflow_collection.created_by,
            engagement=self.workflow_collection_engagement_1,
            start=timezone.now() - timedelta(days=42),
            status=WorkflowCollectionAssignment.IN_PROGRESS,
            workflow_collection=self.workflow_collection,
        )

        # Engagement + Assignment that doesn't get closed due to Collection
        # being ACTIVITY
        self.workflow_collection_engagement_2 = (
            WorkflowCollectionEngagement.objects.create(
                workflow_collection=self.workflow_collection2,
                user=self.workflow_collection2.created_by,
                started=timezone.now() - timedelta(days=32),
            )
        )

        self.assignment_2 = WorkflowCollectionAssignmentFactory(
            engagement=self.workflow_collection_engagement_2,
            user=self.workflow_collection2.created_by,
            status=WorkflowCollectionAssignment.IN_PROGRESS,
            workflow_collection=self.workflow_collection2,
        )

        # Engagement + Assignment that doesn't get closed because the
        # engagement is finished.
        self.user_3 = UserFactory(username="user_3")
        self.workflow_collection_engagement_3 = (
            WorkflowCollectionEngagement.objects.create(
                workflow_collection=self.workflow_collection,
                user=self.user_3,
                started=timezone.now() - timedelta(days=42),
                finished=timezone.now() - timedelta(days=15),
            )
        )
        self.assignment_3 = WorkflowCollectionAssignmentFactory(
            engagement=self.workflow_collection_engagement_3,
            status=WorkflowCollectionAssignment.CLOSED_COMPLETE,
            user=self.user_3,
            workflow_collection=self.workflow_collection,
        )

        # Engagement + Assignment that doesn't get closed because the
        # assignment is not active.
        self.user_4 = UserFactory(username="user_4")
        self.workflow_collection_engagement_4 = (
            WorkflowCollectionEngagement.objects.create(
                workflow_collection=self.workflow_collection,
                user=self.user_4,
                started=timezone.now() - timedelta(days=41),
            )
        )
        self.assignment_4 = WorkflowCollectionAssignmentFactory(
            user=self.user_4,
            engagement=self.workflow_collection_engagement_4,
            status=WorkflowCollectionAssignment.CLOSED_COMPLETE,
            workflow_collection=self.workflow_collection,
        )

        # Engagement + Assignment that gets closed because the
        # engagement is finished.
        self.user_5 = UserFactory(username="user_5")
        self.workflow_collection_engagement_5 = (
            WorkflowCollectionEngagement.objects.create(
                workflow_collection=self.workflow_collection,
                user=self.user_5,
                started=timezone.now() - timedelta(days=3),
                finished=timezone.now() - timedelta(days=15),
            )
        )
        self.assignment_5 = WorkflowCollectionAssignmentFactory(
            engagement=self.workflow_collection_engagement_5,
            status=WorkflowCollectionAssignment.IN_PROGRESS,
            start=timezone.now() - timedelta(days=4),
            user=self.user_5,
            workflow_collection=self.workflow_collection,
        )

    def test_command__success(self):
        """
        Demonstrate that if an 'active' WorkflowCollectionAssignment has an
        open WorkflowCollectionEngagement that is more than 30
        days old and a WorkflowCollection that is 'SURVEY' then the
        assignment gets closed. Hasta la vista, Baby!
        """
        assignment_to_change = WorkflowCollectionAssignment.objects.get(
            id=self.assignment_1.id
        )
        self.assertEqual(assignment_to_change.status, "IN_PROGRESS")

        out = StringIO()
        call_command("assignment_terminator", days_old="30", type="SURVEY", stdout=out)

        assignment_to_change.refresh_from_db()
        self.assertEqual(assignment_to_change.status, "CLOSED_INCOMPLETE")

    def test_command__dont_update_old_activity(self):
        """
        Demonstrate that if an 'active' WorkflowCollectionAssignment has an
        open WorkflowCollectionEngagement that is more than 30
        days old and a WorkflowCollection that is 'ACTIVITY' then the
        assignment DOES NOT get closed.
        """
        assignment = WorkflowCollectionAssignment.objects.get(id=self.assignment_2.id)
        self.assertEqual(assignment.status, "IN_PROGRESS")

        out = StringIO()
        call_command("assignment_terminator", days_old="30", type="SURVEY", stdout=out)

        assignment.refresh_from_db()
        self.assertEqual(assignment.status, "IN_PROGRESS")

    def test_command__dont_update_finished_survey(self):
        """
        Demonstrate that if an 'active' WorkflowCollectionAssignment has a
        WorkflowCollectionEngagement that is more than 30
        days old but finished then the assignment DOES NOT get closed.
        """
        assignment = WorkflowCollectionAssignment.objects.get(id=self.assignment_3.id)
        self.assertEqual(assignment.status, "CLOSED_COMPLETE")

        out = StringIO()
        call_command("assignment_terminator", days_old="30", type="SURVEY", stdout=out)

        assignment.refresh_from_db()
        self.assertEqual(assignment.status, "CLOSED_COMPLETE")

    def test_command__dont_update_inactive_survey(self):
        """
        Demonstrate that if an 'inactive' WorkflowCollectionAssignment has an
        open WorkflowCollectionEngagement that is more than 30
        days old and a WorkflowCollection that is 'SURVEY' then the
        assignment DOES NOT get closed.
        """
        assignment = WorkflowCollectionAssignment.objects.get(id=self.assignment_4.id)
        self.assertEqual(assignment.status, "CLOSED_COMPLETE")

        out = StringIO()
        call_command("assignment_terminator", days_old="30", type="SURVEY", stdout=out)

        assignment.refresh_from_db()
        self.assertEqual(assignment.status, "CLOSED_COMPLETE")

    def test_command__update_active_survey_finished_engagement(self):
        """
        Demonstrate that if an 'active' WorkflowCollectionAssignment has a
        closed WorkflowCollectionEngagement and a WorkflowCollection that is
        'SURVEY' then the assignment DOES get closed.
        """
        assignment = WorkflowCollectionAssignment.objects.get(id=self.assignment_5.id)
        self.assertEqual(assignment.status, "IN_PROGRESS")

        out = StringIO()
        call_command("assignment_terminator", days_old="30", type="SURVEY", stdout=out)

        assignment.refresh_from_db()
        self.assertEqual(assignment.status, "CLOSED_COMPLETE")

    def test_command__set_finished_time(self):
        user = UserFactory()
        workflow_collection = WorkflowCollectionFactory(category="SURVEY")
        wce = WorkflowCollectionEngagementFactory(
            workflow_collection=workflow_collection,
            user=user,
            started=timezone.now() - timedelta(days=300),
            finished=None,
        )
        assignment = WorkflowCollectionAssignmentFactory(
            workflow_collection=workflow_collection,
            user=user,
            engagement=wce,
            start=timezone.now() - timedelta(days=300),
            status=WorkflowCollectionAssignment.IN_PROGRESS,
        )

        call_command(
            "assignment_terminator", days_old="30", type="SURVEY", stdout=StringIO()
        )

        assignment.refresh_from_db()
        wce.refresh_from_db()

        self.assertEqual(
            assignment.status, WorkflowCollectionAssignment.CLOSED_INCOMPLETE
        )
        self.assertIsNotNone(wce.finished)

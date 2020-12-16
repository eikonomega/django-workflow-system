from datetime import timedelta

from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone
from django.utils.six import StringIO

from website.api_v2.tests.factories import (
    WorkflowCollectionAssignmentFactory,
    WorkflowCollectionAssignment2Factory, UserFactory)
from website.workflows.models import (WorkflowCollectionEngagement,
                                      WorkflowCollectionAssignment)

from website.api_v2.tests.factories.workflows.workflow_collection import (
    WorkflowCollectionFactory, WorkflowCollection2Factory)

import website.api_v3.tests.factories as factories



class TestCommand(TestCase):

    def setUp(self):
        self.workflow_collection = WorkflowCollectionFactory()
        self.workflow_collection2 = WorkflowCollection2Factory()

        # Engagement + Assignment that gets closed
        self.workflow_collection_engagement_1 = \
            WorkflowCollectionEngagement.objects.create(
                workflow_collection=self.workflow_collection,
                user=self.workflow_collection.created_by,
                started=timezone.now()-timedelta(days=42))
        self.assignment_1 = WorkflowCollectionAssignmentFactory(
            engagement=self.workflow_collection_engagement_1,
            assigned_on=timezone.now()-timedelta(days=42),
            status=WorkflowCollectionAssignment.IN_PROGRESS)

        # Engagement + Assignment that doesn't get closed due to Collection
        # being ACTIVITY
        self.workflow_collection_engagement_2 = \
            WorkflowCollectionEngagement.objects.create(
                workflow_collection=self.workflow_collection2,
                user=self.workflow_collection2.created_by,
                started=timezone.now()-timedelta(days=32))

        self.assignment_2 = WorkflowCollectionAssignment2Factory(
            engagement=self.workflow_collection_engagement_2,
            status=WorkflowCollectionAssignment.IN_PROGRESS)

        # Engagement + Assignment that doesn't get closed because the
        # engagement is finished.
        self.user_3 = UserFactory(username='user_3')
        self.workflow_collection_engagement_3 = \
            WorkflowCollectionEngagement.objects.create(
                workflow_collection=self.workflow_collection,
                user=self.user_3,
                started=timezone.now()-timedelta(days=42),
                finished=timezone.now()-timedelta(days=15))
        self.assignment_3 = WorkflowCollectionAssignment2Factory(
            engagement=self.workflow_collection_engagement_3,
            status=WorkflowCollectionAssignment.CLOSED_COMPLETE,
            user=self.user_3)

        # Engagement + Assignment that doesn't get closed because the
        # assignment is not active.
        self.user_4 = UserFactory(username='user_4')
        self.workflow_collection_engagement_4 = \
            WorkflowCollectionEngagement.objects.create(
                workflow_collection=self.workflow_collection,
                user=self.user_4,
                started=timezone.now() - timedelta(days=41))
        self.assignment_4 = WorkflowCollectionAssignmentFactory(
            user=self.user_4,
            engagement=self.workflow_collection_engagement_4,
            status=WorkflowCollectionAssignment.CLOSED_COMPLETE)

        # Engagement + Assignment that gets closed because the
        # engagement is finished.
        self.user_5 = UserFactory(username='user_5')
        self.workflow_collection_engagement_5 = \
            WorkflowCollectionEngagement.objects.create(
                workflow_collection=self.workflow_collection,
                user=self.user_5,
                started=timezone.now() - timedelta(days=3),
                finished=timezone.now() - timedelta(days=15))
        self.assignment_5 = WorkflowCollectionAssignmentFactory(
            engagement=self.workflow_collection_engagement_5,
            status=WorkflowCollectionAssignment.IN_PROGRESS,
            assigned_on= timezone.now() - timedelta(days=4),
            user=self.user_5)

    def test_command__success(self):
        """
        Demonstrate that if an 'active' WorkflowCollectionAssignment has an
        open WorkflowCollectionEngagement that is more than 30
        days old and a WorkflowCollection that is 'SURVEY' then the
        assignment gets closed. Hasta la vista, Baby!
        """
        assignment_to_change = WorkflowCollectionAssignment.objects.get(id=self.assignment_1.id)
        self.assertEqual(assignment_to_change.status, 'IN_PROGRESS')

        out = StringIO()
        call_command('assignment_terminator', stdout=out)

        assignment_to_change.refresh_from_db()
        self.assertEqual(assignment_to_change.status, 'CLOSED_INCOMPLETE')

    def test_command__dont_update_old_activity(self):
        """
        Demonstrate that if an 'active' WorkflowCollectionAssignment has an
        open WorkflowCollectionEngagement that is more than 30
        days old and a WorkflowCollection that is 'ACTIVITY' then the
        assignment DOES NOT get closed.
        """
        assignment = WorkflowCollectionAssignment.objects.get(
            id=self.assignment_2.id)
        self.assertEqual(assignment.status, 'IN_PROGRESS')

        out = StringIO()
        call_command('assignment_terminator', stdout=out)

        assignment.refresh_from_db()
        self.assertEqual(assignment.status, 'IN_PROGRESS')

    def test_command__dont_update_finished_survey(self):
        """
        Demonstrate that if an 'active' WorkflowCollectionAssignment has a
        WorkflowCollectionEngagement that is more than 30
        days old but finished then the assignment DOES NOT get closed.
        """
        assignment = WorkflowCollectionAssignment.objects.get(
            id=self.assignment_3.id)
        self.assertEqual(assignment.status, 'CLOSED_COMPLETE')

        out = StringIO()
        call_command('assignment_terminator', stdout=out)

        assignment.refresh_from_db()
        self.assertEqual(assignment.status, 'CLOSED_COMPLETE')

    def test_command__dont_update_inactive_survey(self):
        """
        Demonstrate that if an 'inactive' WorkflowCollectionAssignment has an
        open WorkflowCollectionEngagement that is more than 30
        days old and a WorkflowCollection that is 'SURVEY' then the
        assignment DOES NOT get closed.
        """
        assignment = WorkflowCollectionAssignment.objects.get(
            id=self.assignment_4.id)
        self.assertEqual(assignment.status, 'CLOSED_COMPLETE')

        out = StringIO()
        call_command('assignment_terminator', stdout=out)

        assignment.refresh_from_db()
        self.assertEqual(assignment.status, 'CLOSED_COMPLETE')

    def test_command__update_active_survey_finished_engagement(self):
        """
        Demonstrate that if an 'active' WorkflowCollectionAssignment has a
        closed WorkflowCollectionEngagement and a WorkflowCollection that is
        'SURVEY' then the assignment DOES get closed.
        """
        assignment = WorkflowCollectionAssignment.objects.get(
            id=self.assignment_5.id)
        self.assertEqual(assignment.status, 'IN_PROGRESS')

        out = StringIO()
        call_command('assignment_terminator', stdout=out)

        assignment.refresh_from_db()
        self.assertEqual(assignment.status, 'CLOSED_COMPLETE')

    def test_command__set_finished_time(self):
        user = factories.UserFactory()
        workflow_collection = factories.WorkflowCollectionFactory(
            category='SURVEY'
        )
        wce = factories.WorkflowCollectionEngagementFactory(
            workflow_collection=workflow_collection,
            user=user,
            started=timezone.now() - timedelta(days=300),
            finished=None,
        )
        assignment = factories.WorkflowCollectionAssignmentFactory(
            workflow_collection=workflow_collection,
            user=user,
            engagement=wce,
            assigned_on=timezone.now() - timedelta(days=300),
            status=WorkflowCollectionAssignment.IN_PROGRESS
        )

        call_command('assignment_terminator', stdout=StringIO())

        assignment.refresh_from_db()
        wce.refresh_from_db()

        self.assertEqual(assignment.status, WorkflowCollectionAssignment.CLOSED_INCOMPLETE)
        self.assertIsNotNone(wce.finished)


class TestCommandTwo(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.demographics_survey_welcome_collection = factories.WorkflowCollectionFactory(
            code='demographics_survey_welcome_collection',
            category='SURVEY',
        )

    def setUp(self) -> None:
        self.user = factories.UserFactory()

    def call_command(self):
        call_command("assignment_terminator")

    def test_excludes_demographics_survey_welcome_collection(self):
        assignment = factories.WorkflowCollectionAssignmentFactory(
            user=self.user,
            workflow_collection=self.demographics_survey_welcome_collection,
            status=WorkflowCollectionAssignment.ASSIGNED,
            assigned_on=(timezone.now() - timedelta(300)).date(),
        )

        self.call_command()

        assignment_after = WorkflowCollectionAssignment.objects.get(pk=assignment.pk)

        self.assertEqual(assignment_after.status, WorkflowCollectionAssignment.ASSIGNED)

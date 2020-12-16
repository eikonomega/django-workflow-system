from dateutil.relativedelta import relativedelta

from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone
from django.utils.six import StringIO

from website.api_v2.tests.factories import (
    WorkflowCollectionAssignmentFactory)
from website.api_v2.tests.factories.workflows.workflow_collection import (
    WorkflowCollectionFactory, WorkflowCollection2Factory)
from website.workflows.models import (WorkflowCollectionEngagement,
                                      WorkflowCollectionAssignment)
from website.notifications.models import Target, UserTarget, Notification
from website.workflows.management.commands.open_assignment_notification import (
    Command)


cmd = Command()


class TestCommand(TestCase):

    def setUp(self):
        self.workflow_collection = WorkflowCollectionFactory(name='Wellbeing Assessment', code='demographics_survey_welcome_collection')
        self.workflow_collection2 = WorkflowCollection2Factory()
        print(self.workflow_collection.name)
        # Engagement + Assignment that gets closed
        self.workflow_collection_engagement = \
            WorkflowCollectionEngagement.objects.create(
                workflow_collection=self.workflow_collection,
                user=self.workflow_collection.created_by,
                started=timezone.now()-relativedelta(days=18))

        self.assignment = WorkflowCollectionAssignmentFactory(
            user=self.workflow_collection.created_by,
            workflow_collection=self.workflow_collection,
            engagement=self.workflow_collection_engagement,
            status=WorkflowCollectionAssignment.IN_PROGRESS,
            assigned_on=timezone.now().date()-relativedelta(days=20))

        self.workflow_collection_engagement_2 = \
            WorkflowCollectionEngagement.objects.create(
                workflow_collection=self.workflow_collection2,
                user=self.workflow_collection2.created_by,
                started=timezone.now()-relativedelta(days=15))

        # Ensure no notification is sent for Completed Assignments
        self.assignment_2 = WorkflowCollectionAssignmentFactory(
            user=self.workflow_collection.created_by,
            workflow_collection=self.workflow_collection2,
            engagement=self.workflow_collection_engagement_2,
            status=WorkflowCollectionAssignment.CLOSED_COMPLETE,
            assigned_on=timezone.now().date()-relativedelta(days=19))

        self.target = Target.objects.create(
            name="Expo",
            class_name="Expo")

        self.user_target = UserTarget.objects.create(
            user=self.workflow_collection_engagement.user,
            target=self.target,
            user_target_id='Does not need to be real.',
            user_target_friendly_name="Dangle's Toasty Toasty Toaster")

    def test_command__success(self):
        """
        Demonstrate that if a user has an Assignment that is over
        7 days old and has not yet been completed, a notification
        will be created for the user.
        """

        pre_command = Notification.objects.all()
        self.assertEqual(len(pre_command), 0)

        out = StringIO()
        call_command('open_assignment_notification', stdout=out)

        post_command = Notification.objects.all()
        self.assertEqual(len(post_command), 2)

        # Updating the Notification as DELIVERED to test that a duplicate
        # entry is not made.
        Notification.objects.all().update(
            status='DELIVERED',
            scheduled_delivery=timezone.now()-relativedelta(days=3),
            attempted_delivery=timezone.now()-relativedelta(days=3))

        # Calling the command a second time here to ensure no
        # duplicate notification is created.
        call_command('open_assignment_notification', stdout=out)

        no_duplicates = Notification.objects.all()
        self.assertEqual(len(no_duplicates), 2)

        # Updating the Notification date to have been sent 16 days ago.
        Notification.objects.all().update(
            status='DELIVERED',
            scheduled_delivery=timezone.now()-relativedelta(days=16),
            attempted_delivery=timezone.now()-relativedelta(days=16))

        call_command('open_assignment_notification', stdout=out)

        no_duplicates = Notification.objects.all()
        self.assertEqual(len(no_duplicates), 4)

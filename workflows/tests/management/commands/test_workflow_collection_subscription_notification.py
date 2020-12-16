import datetime

from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone
from django.utils.six import StringIO

from localtime.models import TimeZone
from website.workflows.models import (
    Workflow,
    WorkflowAuthor,
    WorkflowCollection,
    WorkflowCollectionSubscription,
    WorkflowCollectionSubscriptionSchedule
)
from website.notifications.models import (
    Notification,
    Target,
    UserTarget)


class TestCommand(TestCase):

    def setUp(self):
        self.user = User.objects.create(
            username='STEVE!!',
            email="STEVES!!email.nd.edu",
            password='password',
        )

        TimeZone.objects.create(user=self.user, timezone_str="UTC")

        self.author = WorkflowAuthor.objects.create(
            user=self.user,
            title="little jon",
            image='steve!?!.png',
            biography='I did stuff?')

        self.workflow = Workflow.objects.create(
            code="workflow_code_I",
            name="workflow code I",
            version=1,
            image="look_at_me.png",
            author=self.author,
            created_by=self.user)

        self.workflow_collection = WorkflowCollection.objects.create(
            code="workflow_collection_I",
            name="workflow collection I",
            ordered=True,
            version=1,
            created_by=self.user,
            category="activity",
            assignment_only=False,
            active=True,
        )

        self.workflow_collection_subscription = WorkflowCollectionSubscription.objects.create(
            workflow_collection=self.workflow_collection,
            user=self.user,
            active=True)

        self.day_of_week = timezone.now().weekday()
        self.workflow_collection_subscription_schedule = WorkflowCollectionSubscriptionSchedule.objects.create(
            workflow_collection_subscription=self.workflow_collection_subscription,
            time_of_day="11:12:00",
            day_of_week=self.day_of_week,
            weekly_interval=1)

        self.notification_target = Target.objects.create(
            name="Expo",
            class_name="Expo")

        self.notification_user_target = UserTarget.objects.create(
            user=self.user,
            target=self.notification_target,
            user_target_id=str(self.user.id),
            user_target_friendly_name="Steve phone")

        # setting up two workflow collections with same date/time for
        # notification.  Currently it is fine if two separate workflow
        # collections have same day and time for notification.
        self.workflow_collection2 = WorkflowCollection.objects.create(
            code="workflow_collection_II",
            name="workflow collection II",
            ordered=True,
            version=1,
            created_by=self.user,
            category="activity",
            assignment_only=False,
            active=True,
        )

        self.workflow_collection_subscription2 = WorkflowCollectionSubscription.objects.create(
            workflow_collection=self.workflow_collection2,
            user=self.user,
            active=True)

        self.workflow_collection_subscription_schedule2 = WorkflowCollectionSubscriptionSchedule.objects.create(
            workflow_collection_subscription=self.workflow_collection_subscription2,
            time_of_day="11:12:00",
            day_of_week=self.day_of_week,
            weekly_interval=1)

    def test_command_success(self):
        """
        Demonstrate that the correct number of Notifications are created when
        the command is run.
        """
        notification = Notification.objects.all()
        self.assertEqual(0, len(notification))

        out = StringIO()
        call_command(
            'workflow_collection_subscription_notification',
            stdout=out)

        notification = Notification.objects.all()
        self.assertEqual(2, len(notification))

    def test_command__redundant_invocation(self):
        """
        If workflow collection notification is called multiple times
        on the same day, it doesn't duplicate existing entries.
        """
        notification = Notification.objects.all()
        self.assertEqual(0, len(notification))

        call_command('workflow_collection_subscription_notification')

        notification = Notification.objects.all()
        self.assertEqual(2, len(notification))

        call_command('workflow_collection_subscription_notification')

        notification = Notification.objects.all()
        self.assertEqual(2, len(notification))


    def test_command__notifications(self):
        call_command('workflow_collection_subscription_notification')

        notifications = Notification.objects.all()
        self.assertEqual(2, notifications.count())

        for notification in notifications:
            self.assertGreaterEqual(notification.scheduled_delivery, timezone.now())
            delivery_hour = notification.scheduled_delivery.astimezone(self.user.timezone.tzinfo).time()
            self.assertEqual(delivery_hour, datetime.time(11, 12, 0))



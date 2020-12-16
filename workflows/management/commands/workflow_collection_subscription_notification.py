from django.core.management.base import BaseCommand
from django.conf import settings
from django.urls import reverse

import website
from localtime.models import TimeZone
from website.notifications.utils.notifications_creators import create_expo_notifications
from ...models import WorkflowCollectionSubscriptionSchedule


# logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Create Workflow Notification records for the current day.

    Notes
    -----
    Workflow schedules are meant to be assigned each day a little after
    midnight. While it is possible to run this command via manage.py, it will
    normally be executed via CRON.

    You can see the schedule that it will run on by looking at the
    CRONJOBS setting in the QA/Production settings files.
    """

    help = __doc__

    def handle(self, *args, **options):
        """
        This method is what is actually run via python manage.py
        """

        # Step 1: Retrieve all currently active workflow schedules.
        workflow_collection_schedules = WorkflowCollectionSubscriptionSchedule.objects.filter(
            workflow_collection_subscription__active=True
        )

        # Step 2: Loop through each workflow collection subscription to get to
        # workflow subscription
        for collection_subscription_schedule in workflow_collection_schedules:

            workflow_collection_subscription = (
                collection_subscription_schedule.workflow_collection_subscription
            )
            user = workflow_collection_subscription.user

            if not hasattr(user, "timezone"):
                # EST, for us
                TimeZone.objects.create(user=user, timezone_str=settings.TIME_ZONE)

            if collection_subscription_schedule.day_of_week == user.timezone.weekday():
                self.stdout.write(f"Processing {workflow_collection_subscription}")

                scheduled_delivery_datetime = user.timezone.next_clock_time(
                    collection_subscription_schedule.time_of_day
                )

                data = {
                    "event": "WorkflowSubscriptionReminder",
                    "event_details": {
                        "workflow_collection_subscription_url": website.get_site_url()
                        + reverse(
                            viewname="user-workflow-collection-subscription-v3",
                            kwargs={"id": workflow_collection_subscription.id},
                        ),
                        "workflow_collection_url": website.get_site_url()
                        + reverse(
                            viewname="workflow-collection-v3",
                            kwargs={
                                "id": workflow_collection_subscription.workflow_collection.id
                            },
                        ),
                    },
                }

                create_expo_notifications(
                    user=user,
                    title=workflow_collection_subscription.workflow_collection.name,
                    body=f"Your Workflow: {workflow_collection_subscription.workflow_collection.name} is ready!",
                    scheduled_delivery=scheduled_delivery_datetime,
                    extra={"data": data},
                )
            else:
                self.stdout.write(f"Skipping {workflow_collection_subscription}")

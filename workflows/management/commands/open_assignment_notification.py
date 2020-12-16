from datetime import time

from dateutil.relativedelta import relativedelta

from django.core.management import BaseCommand
from django.db.models import Q
from django.utils import timezone

from website import get_site_url
from localtime.models import TimeZone
from website.notifications.models import Notification
from website.notifications.utils.notifications_creators import (
    create_email_notifications,
    create_expo_notifications,
)
from website.notifications.utils.opt_out_link import get_opt_out_link
from website.workflows.models import WorkflowCollectionAssignment


class Command(BaseCommand):
    """
    This command's purpose is to notify any user that has
    been assigned a survey WorkflowCollection to complete and has
    not yet completed the assignment/engagement.

    We want to leave the assignment open and periodically
    notify the user that they have an open assignment.
    """

    def handle(self, *args, **options):
        """
        This method is what is actually run via python manage.py.
        """
        now = timezone.now()

        open_assignments = WorkflowCollectionAssignment.objects.filter(
            Q(status="ASSIGNED") | Q(status="IN_PROGRESS"),
            assigned_on__lte=timezone.now() - relativedelta(days=15),
        )

        for open_assignment in open_assignments:
            user_has_been_notified = Notification.objects.filter(
                related_object_uuid=open_assignment.id,
                scheduled_delivery__gte=timezone.now() - relativedelta(days=15),
            )

            if not user_has_been_notified:
                # Create a reminder notification to be sent around 10am.
                user = open_assignment.user
                TimeZone.objects.get_or_create(user=user)
                ten_am = user.timezone.next_clock_time(time(10), now)
                collection_name = open_assignment.workflow_collection.name
                create_expo_notifications(
                    open_assignment.user,
                    collection_name,
                    f"Hi {user.first_name}, just a reminder that you have an open {collection_name}.",
                    ten_am,
                    related_object_uuid=open_assignment.id,
                )

                if open_assignment.workflow_collection.code == 'demographics_survey_welcome_collection':

                    # Create an email reminder as well.
                    create_email_notifications(
                        user=user,
                        title=f"Reminder Complete your WorkWell Wellbeing Assessment Today",
                        template_path=(
                            "user_signup/emails/wellbeing_assessment_reminder.html"
                        ),
                        scheduled_delivery=ten_am,
                        related_object_uuid=open_assignment.id,
                        **{
                            "db_user": open_assignment.user,
                            "SITE_URL": get_site_url(),
                            "opt_out_link": get_opt_out_link(open_assignment.user),
                        },
                    )

                print(
                    f"Reminder notifications created for {user.username} - {collection_name}"
                )

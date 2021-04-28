from django.core.management import BaseCommand
from django.contrib.auth.models import Group
from django.utils import timezone

from ...models import WorkflowCollectionAssignment, WorkflowCollection


class Command(BaseCommand):
    """
    This command generates WorkflowCollection Assignments for members of a specific group.
    """

    def add_arguments(self, parser):
        parser.add_argument(
            "-wc",
            "--workflow_collection",
            type=str,
            required=True,
            help="The name of the WorkflowCollection this assignment will be for.",
        )
        parser.add_argument(
            "-g",
            "--groups",
            type=str,
            required=True,
            help="Which groups members. For multiple groups use a comma seperated list of the groups name . Ex: egg_group,sandwich_group",
        )

    def handle(self, *args, **options):
        """
        This is what is being run by manage.py
        """
        if options["workflow_collection"]:
            collection_name = options["workflow_collection"]

        if options["groups"]:
            groups_str = options["groups"].split(",")
            group_names = [item for item in groups_str]

        # Let's check that the WorkflowCollection even exists
        try:
            workflow_collection = WorkflowCollection.objects.get(
                name__iexact=collection_name
            )
        except WorkflowCollection.DoesNotExist:
            print(f"No WorkflowCollection found with name {collection_name}.")
            return

        # Get the members of all groups provided
        groups = Group.objects.filter(name__in=group_names)
        # If filter is empty, end this.
        if not groups:
            print(f"No groups found in provided argument '{group_names}'")
            return

        list_of_users = []
        for group in groups:
            for user in group.user_set.all():
                list_of_users.append(user)
        # Get rid of duplicates. ie: User's that belong to multiple groups should only get one assignement.
        clean_list_of_users = set(list_of_users)

        # Now assign all these users this Collection.
        for user in clean_list_of_users:
            WorkflowCollectionAssignment.objects.create(
                workflow_collection=workflow_collection, user=user
            )
            print(
                f"Assignment '{workflow_collection.name} - {user.username}' has been created."
            )

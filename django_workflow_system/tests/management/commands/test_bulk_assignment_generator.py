# from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from io import StringIO

#
#
# from ....api.tests.factories.workflows.workflow_collection import (
#     WorkflowCollectionFactory)
# from ....models import WorkflowCollectionAssignment
#
#
from django_workflow_system.api.tests.factories import WorkflowCollectionFactory
from django_workflow_system.models import WorkflowCollectionAssignment


class TestCommand(TestCase):
    def setUp(self):
        User = get_user_model()
        self.workflow_collection = WorkflowCollectionFactory()

        self.user1 = User.objects.create_user(
            username="StaffMember",
            email="staff.member@nd.edu",
            first_name="Staff",
            last_name="Member",
            password="I'm so balanced in my work/life!",
            is_staff=True,
        )
        self.user2 = User.objects.create_user(
            username="EggMember",
            email="egg.member@nd.edu",
            first_name="Egg",
            last_name="Member",
            password="I'm so balanced in my egg",
            is_staff=True,
        )
        self.user3 = User.objects.create_user(
            username="Kermit",
            email="kfrog@nd.edu",
            first_name="Kermit",
            last_name="The Frog",
            password="RainbowConnection.?!",
            is_staff=False,
        )

    def test_command__success(self):
        """
        Demonstrate that if the groups and WorkflowCollection provided are valid,
        that the assignments will be created.
        """
        # Create a group
        group = Group.objects.create(name="FrogBois")
        # Populate with our users
        group.user_set.add(self.user1, self.user2, self.user3)

        # Check the count of assignments prior
        assignments_prior = WorkflowCollectionAssignment.objects.all()
        self.assertEqual(len(assignments_prior), 0)

        out = StringIO()
        call_command(
            "bulk_assignment_generator",
            workflow_collection=self.workflow_collection.name,
            groups="FrogBois",
            stdout=out,
        )

        # Check that assignments have been created for all 3 users.
        assignments_post = WorkflowCollectionAssignment.objects.all()
        self.assertEqual(len(assignments_post), 3)

    def test_command__no_group_match(self):
        """
        Demonstrate that if no groups are found with the provided name,
        no assignments are created
        """
        # Check the count of assignments prior
        assignments_prior = WorkflowCollectionAssignment.objects.all()
        self.assertEqual(len(assignments_prior), 0)

        out = StringIO()
        call_command(
            "bulk_assignment_generator",
            workflow_collection=self.workflow_collection.name,
            groups="FrogBois",
            stdout=out,
        )

        # Check that no assignments have been created
        assignments_post = WorkflowCollectionAssignment.objects.all()
        self.assertEqual(len(assignments_post), 0)

    def test_command__no_workflow_match(self):
        """
        Demonstrate that if a workflow collection isn't found with the provided name,
        no assignments are created
        """
        # Create a group
        group = Group.objects.create(name="FrogBois")
        # Populate with our users
        group.user_set.add(self.user1, self.user2, self.user3)
        # Check the count of assignments prior
        assignments_prior = WorkflowCollectionAssignment.objects.all()
        self.assertEqual(len(assignments_prior), 0)

        out = StringIO()
        call_command(
            "bulk_assignment_generator",
            workflow_collection="Spaghetti",
            groups="FrogBois",
            stdout=out,
        )

        # Check that no assignments have been created
        assignments_post = WorkflowCollectionAssignment.objects.all()
        self.assertEqual(len(assignments_post), 0)

    def test_command__user_in_multiple_groups(self):
        """
        Demonstrate that if a User is in multiple groups that the command is run on,
        only one assignment is created for that user.
        """
        group1 = Group.objects.create(name="Land")
        group1.user_set.add(self.user1)
        group2 = Group.objects.create(name="Sand")
        group2.user_set.add(self.user1)
        group3 = Group.objects.create(name="Hand")
        group3.user_set.add(self.user1)

        # Check the count of assignments prior
        assignments_prior = WorkflowCollectionAssignment.objects.all()
        self.assertEqual(len(assignments_prior), 0)

        out = StringIO()
        call_command(
            "bulk_assignment_generator",
            workflow_collection=self.workflow_collection.name,
            groups="Land,Hand,Sand",
            stdout=out,
        )
        # Check that only 1 assignment has been created
        assignments_post = WorkflowCollectionAssignment.objects.all()
        self.assertEqual(len(assignments_post), 1)

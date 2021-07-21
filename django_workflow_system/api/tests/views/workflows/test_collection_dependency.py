"""Unit test for collection dependency."""
from django.test import TestCase

from rest_framework.test import APIRequestFactory

from django_workflow_system.api.tests.factories import (
    UserFactory,
    WorkflowCollectionFactory,
)

from django_workflow_system.api.views.workflows import (
    WorkflowCollectionsView,
)

from django_workflow_system.models import (
    WorkflowCollectionDependency,
    WorkflowCollectionEngagement,
)


class TestWorkflowCollectionsDependencyView(TestCase):
    """Test WorkflowCollectionsDependencyView class."""

    def setUp(self):
        """Unit test set up."""
        self.factory = APIRequestFactory()
        self.view = WorkflowCollectionsView.as_view()

        self.user = UserFactory()

        # set up collections
        self.workflow_collection_1 = WorkflowCollectionFactory()
        self.workflow_collection_2 = WorkflowCollectionFactory()
        self.workflow_collection_3 = WorkflowCollectionFactory()
        self.workflow_collection_4 = WorkflowCollectionFactory()
        self.workflow_collection_5 = WorkflowCollectionFactory()

        # set up dependencies
        self.dependency_1_from_2 = WorkflowCollectionDependency.objects.create(
            source=self.workflow_collection_2, target=self.workflow_collection_1
        )
        # dependency for collection 3
        self.dependency_2_from_3 = WorkflowCollectionDependency.objects.create(
            source=self.workflow_collection_3, target=self.workflow_collection_2
        )
        # dependency for collection 4
        self.dependency_1_from_4 = WorkflowCollectionDependency.objects.create(
            source=self.workflow_collection_4, target=self.workflow_collection_1
        )
        self.dependency_3_from_4 = WorkflowCollectionDependency.objects.create(
            source=self.workflow_collection_4, target=self.workflow_collection_3
        )
        # dependency for collection 5
        self.dependency_1_from_5 = WorkflowCollectionDependency.objects.create(
            source=self.workflow_collection_5, target=self.workflow_collection_1
        )
        self.dependency_3_from_5 = WorkflowCollectionDependency.objects.create(
            source=self.workflow_collection_5, target=self.workflow_collection_3
        )
        self.dependency_2_from_5 = WorkflowCollectionDependency.objects.create(
            source=self.workflow_collection_5, target=self.workflow_collection_2
        )
        self.dependency_4_from_5 = WorkflowCollectionDependency.objects.create(
            source=self.workflow_collection_5, target=self.workflow_collection_4
        )

        # set up engagement
        self.engagement_1 = WorkflowCollectionEngagement.objects.create(
            user=self.user,
            workflow_collection=self.workflow_collection_1,
            started="2021-07-20 00:00:00",
            finished="2021-07-20 00:00:00",
        )
        self.engagement_2 = WorkflowCollectionEngagement.objects.create(
            user=self.user,
            workflow_collection=self.workflow_collection_2,
            started="2021-07-20 00:00:00",
        )
        self.engagement_3 = WorkflowCollectionEngagement.objects.create(
            user=self.user,
            workflow_collection=self.workflow_collection_3,
            started="2021-07-20 00:00:00",
            finished="2021-07-20 00:00:00",
        )
        self.engagement_4 = WorkflowCollectionEngagement.objects.create(
            user=self.user,
            workflow_collection=self.workflow_collection_4,
            started="2021-07-20 00:00:00",
        )

    def test_no_dependencies(self):
        """Test a collection with no dependencies returns true for "status"."""
        request = self.factory.get("/workflows/collections/")
        request.user = self.user
        response = self.view(request)
        self.assertEqual(response.data[0]["dependencies_completed"], True)

    def test_unmet_dependencies(self):
        """Test a collection with unmet dependencies returns false for "status".

        workflow_collection_3 has dependencies workflow_collection_1(finished) and workflow_collection_2(not finished).
        """
        request = self.factory.get("/workflows/collections/")
        request.user = self.user
        response = self.view(request)
        self.assertEqual(response.data[2]["dependencies_completed"], False)

    def test_met_dependencies(self):
        """Test a collection with multiple met dependencies returns true for "status".

        workflow_collection_4 has dependencies workflow_collection_1(finished) and workflow_collection_3(finished).
        """
        request = self.factory.get("/workflows/collections/")
        request.user = self.user
        response = self.view(request)
        self.assertEqual(response.data[3]["dependencies_completed"], True)

    def test_met_unmet_dependencies(self):
        """Test a collection with multiple met/unmet dependencies returns false for "status".

        workflow_collection_5 has dependencies workflow_collection_1(finished) and workflow_collection_3(finished)
        workflow_collection_2(not finished) and workflow_collection_3(not finished).
        """
        request = self.factory.get("/workflows/collections/")
        request.user = self.user
        response = self.view(request)
        self.assertEqual(response.data[4]["dependencies_completed"], False)

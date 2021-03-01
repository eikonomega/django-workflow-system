from django.test import TestCase
from rest_framework import status

from rest_framework.test import APIRequestFactory

from ....tests import factories
from ....views.workflows import WorkflowCollectionsView


class TestWorkflowCollectionsView_2(TestCase):
    """Test WorkflowCollectionsView class."""

    maxDiff = 300

    @classmethod
    def setUpTestData(cls):
        cls.recommendable_practice_v1 = factories.WorkflowCollectionFactory(
            active=False, code="recommendable_practice", version=1,
        )
        cls.recommendable_practice_v2 = factories.WorkflowCollectionFactory(
            active=True, code="recommendable_practice", version=2,
        )
        cls.subscribable_practice_v1 = factories.WorkflowCollectionFactory(
            active=False, code="subscribable_practice", version=1,
        )
        cls.subscribable_practice_v2 = factories.WorkflowCollectionFactory(
            active=True, code="subscribable_practice", version=2,
        )
        cls.assignable_practice_v1 = factories.WorkflowCollectionFactory(
            active=False, code="assignable_practice", version=1,
        )
        cls.assignable_practice_v2 = factories.WorkflowCollectionFactory(
            active=True, code="assignable_practice", version=2,
        )

    def setUp(self) -> None:
        self.user = factories.UserFactory()
        self.view = WorkflowCollectionsView.as_view()
        self.factory = APIRequestFactory()

    def test_no_history(self):
        request = self.factory.get("/workflows/collections/")
        request.user = self.user
        response = self.view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        for collection_dict in response.data:
            self.assertIn(
                collection_dict["id"],
                (
                    str(self.assignable_practice_v2.id),
                    str(self.subscribable_practice_v2.id),
                    str(self.recommendable_practice_v2.id),
                ),
            )

    def test_inactive_subscription(self):
        factories.WorkflowCollectionSubscriptionFactory(
            workflow_collection=self.subscribable_practice_v1,
            user=self.user
        )


        request = self.factory.get("/workflows/collections/")
        request.user = self.user
        response = self.view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        for collection_dict in response.data:
            self.assertIn(
                collection_dict["id"],
                (
                    str(self.assignable_practice_v2.id),
                    str(self.subscribable_practice_v1.id),
                    str(self.recommendable_practice_v2.id),
                ),
            )
            if collection_dict["id"] == str(self.subscribable_practice_v1.id):
                self.assertEqual(
                    collection_dict["newer_version"],
                    f"http://testserver/api_v3/workflows/collections/{self.subscribable_practice_v2.id}/"
                )

    def test_inactive_assignment(self):

        factories.WorkflowCollectionAssignmentFactory(
            user=self.user,
            workflow_collection=self.assignable_practice_v1
        )

        request = self.factory.get("/workflows/collections/")
        request.user = self.user
        response = self.view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        for collection_dict in response.data:
            self.assertIn(
                collection_dict["id"],
                (
                    str(self.assignable_practice_v1.id),
                    str(self.subscribable_practice_v2.id),
                    str(self.recommendable_practice_v2.id),
                ),
            )
            if collection_dict["id"] == str(self.assignable_practice_v1.id):
                self.assertEqual(
                    collection_dict["newer_version"],
                    f"http://testserver/api_v3/workflows/collections/{self.assignable_practice_v2.id}/"
                )

    def test_inactive_recommendation(self):

        factories.WorkflowCollectionAssignmentFactory(
            user=self.user,
            workflow_collection=self.recommendable_practice_v1,
        )


        request = self.factory.get("/workflows/collections/")
        request.user = self.user
        response = self.view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        for collection_dict in response.data:
            self.assertIn(
                collection_dict["id"],
                (
                    str(self.assignable_practice_v2.id),
                    str(self.subscribable_practice_v2.id),
                    str(self.recommendable_practice_v1.id),
                ),
            )
            if collection_dict["id"] == str(self.recommendable_practice_v1.id):
                self.assertEqual(
                    collection_dict["newer_version"],
                    f"http://testserver/api_v3/workflows/collections/{self.recommendable_practice_v2.id}/"
                )

    def test_newer_is_inactive(self):

        factories.WorkflowCollectionAssignmentFactory(
            user=self.user,
            workflow_collection=self.recommendable_practice_v1,
        )

        self.recommendable_practice_v2.active = False
        self.recommendable_practice_v2.save()

        request = self.factory.get("/workflows/collections/")
        request.user = self.user
        response = self.view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        for collection_dict in response.data:
            self.assertIn(
                collection_dict["id"],
                (
                    str(self.assignable_practice_v2.id),
                    str(self.subscribable_practice_v2.id),
                    str(self.recommendable_practice_v1.id),
                ),
            )
            if collection_dict["id"] == str(self.recommendable_practice_v1.id):
                self.assertEqual(collection_dict["newer_version"], None)

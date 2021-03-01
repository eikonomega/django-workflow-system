from datetime import datetime, timedelta

import pytz
from django.test import TestCase
from django.utils import timezone
from rest_framework import status

from rest_framework.test import APIRequestFactory

from website.api_v3.views.user.workflows import WorkflowCollectionRecommendationsView
from website.api_v3.views.user.workflows.recommendation import (
    WorkflowCollectionRecommendationView,
)
from website.workflows.models import WorkflowCollectionRecommendation

from .... import factories


class TestWorkflowCollectionRecommendationsView(TestCase):
    """
    Note: This only tests the API endpoint. The collection recommendation system is tested in
    """

    @classmethod
    def setUpTestData(cls):
        cls.url = "/users/self/workflows/recommendations/"
        cls.workflow_collection = factories.WorkflowCollectionFactory()

    def setUp(self) -> None:
        self.view = WorkflowCollectionRecommendationsView.as_view()
        self.factory = APIRequestFactory()
        self.user = factories.UserFactory()

    def test_get__unauthenticated(self):
        """Unauthenticated users cannot access GET method."""
        request = self.factory.get(self.url)
        response = self.view(request)

        self.assertEqual(response.status_code, 403)

    def test_get__authenticated(self):
        """Authenticated users can access GET method."""
        request = self.factory.get(self.url)
        request.user = self.user
        response = self.view(request)

        self.assertEqual(response.status_code, 200)

    def test_get__anything(self):
        request = self.factory.get(self.url)
        request.user = self.user

        factories.WorkflowCollectionRecommendationFactory(user=self.user,)

        response = self.view(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertListEqual(
            ["detail", "workflow_collection", "start", "end"],
            list(response.data[0].keys()),
        )

    def test_get__filter_ended(self):
        request = self.factory.get(self.url)
        request.user = self.user

        factories.WorkflowCollectionRecommendationFactory(
            user=self.user,
            start=timezone.now() - timedelta(10),
            end=timezone.now() - timedelta(5),
        )

        response = self.view(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)

    def test_get__filter_not_started(self):
        request = self.factory.get(self.url)
        request.user = self.user

        factories.WorkflowCollectionRecommendationFactory(
            user=self.user,
            start=timezone.now() + timedelta(5),
            end=timezone.now() + timedelta(10),
        )

        response = self.view(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)

    def test_post__valid_payload(self):
        request = self.factory.post(
            self.url,
            data={
                "workflow_collection": f"http://testserver/api_v3/workflows/collections/{self.workflow_collection.id}/",
                "start": timezone.now(),
                "end": None,
            },
            format="json",
        )
        request.user = self.user
        response = self.view(request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNotNone(response.data["start"])
        self.assertIsNone(response.data["end"])

        self.assertEqual(
            WorkflowCollectionRecommendation.objects.filter(user=self.user).count(), 1
        )

    def test_post__valid_payload__auto_now(self):
        earlier = timezone.now()
        request = self.factory.post(
            self.url,
            data={
                "workflow_collection": f"http://testserver/api_v3/workflows/collections/{self.workflow_collection.id}/",
                # "start": timezone.now(),
                # "end": None,
            },
            format="json",
        )
        request.user = self.user
        response = self.view(request)
        later = timezone.now()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNotNone(response.data["start"])
        self.assertGreaterEqual(datetime.fromisoformat(response.data["start"]), earlier)
        self.assertLessEqual(datetime.fromisoformat(response.data["start"]), later)
        self.assertIsNone(response.data["end"])

        self.assertEqual(
            WorkflowCollectionRecommendation.objects.filter(user=self.user).count(), 1
        )

    def test_post__invalid_payload(self):
        request = self.factory.post(
            self.url,
            data={
                "workflow_collection": f"http://testserver/api_v3/workflows/collections/{self.workflow_collection.id}/",
                "start": timezone.now(),
                "end": timezone.now() - timedelta(days=1),
            },
            format="json",
        )
        request.user = self.user
        response = self.view(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(
            WorkflowCollectionRecommendation.objects.filter(user=self.user).count(), 0
        )


class TestWorkflowCollectionRecommendationView(TestCase):
    """
    Note: This only tests the API endpoint. The collection recommendation system is tested in
    """

    @classmethod
    def setUpTestData(cls):
        cls.url = "/users/self/workflows/recommendations/{}/"

    def setUp(self) -> None:
        self.view = WorkflowCollectionRecommendationView.as_view()
        self.factory = APIRequestFactory()
        self.user = factories.UserFactory()
        self.wcr = factories.WorkflowCollectionRecommendationFactory(user=self.user)
        self.wcr_id = str(self.wcr.id)

    def test_get__unauthenticated(self):
        """Unauthenticated users cannot access GET method."""
        request = self.factory.get(self.url.format(str(self.wcr.id)))
        response = self.view(request)

        self.assertEqual(response.status_code, 403)

    def test_get__authenticated(self):
        """Authenticated users can access GET method."""
        url = self.url.format(self.wcr_id)
        request = self.factory.get(url)
        request.user = self.user

        response = self.view(request, self.wcr_id)
        self.assertEqual(response.status_code, 200)

        for key in [
            "detail",
            "workflow_collection",
            "start",
            "end",
        ]:
            self.assertIn(
                key, response.data,
            )
        self.assertIn(url, response.data["detail"])

    def test_patch__authenticated(self):
        """Authenticated users can access PATCH method."""
        url = self.url.format(self.wcr_id)
        request = self.factory.patch(url, data={"end": timezone.now(),})
        request.user = self.user

        self.assertIsNone(self.wcr.end)

        response = self.view(request, self.wcr_id)
        wcr = WorkflowCollectionRecommendation.objects.get(pk=self.wcr.pk)
        self.assertEqual(response.status_code, 200)

        for key in [
            "detail",
            "workflow_collection",
            "start",
            "end",
        ]:
            self.assertIn(
                key, response.data,
            )

        self.assertIsNotNone(response.data["end"])
        self.assertIsNotNone(wcr.end)

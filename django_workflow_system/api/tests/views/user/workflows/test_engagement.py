import dateutil
from django.test import TestCase

from django.utils import timezone
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APIRequestFactory

from django_workflow_system.api.tests.factories import (
    UserFactory,
    WorkflowCollectionEngagementFactory,
    WorkflowCollectionFactory,
)
from django_workflow_system.api.views.user.workflows import (
    WorkflowCollectionEngagementView,
)


class TestWorkflowCollectionEngagementView(TestCase):
    """Test WorkflowCollectionEngagementView."""

    def setUp(self):
        self.view = WorkflowCollectionEngagementView.as_view()
        self.view_url = "/users/self/workflows/engagements/{}"
        self.factory = APIRequestFactory()

        self.workflow_collection = WorkflowCollectionFactory(workflow_set=[{}])
        self.user_with_engagement = UserFactory()
        #         self.user_with_engagement2 = factories.UserFactory()
        self.user_without_engagement = UserFactory(username="Engagementless")
        self.workflow_engagement = WorkflowCollectionEngagementFactory(
            user=self.user_with_engagement,
            workflow_collection=self.workflow_collection,
        )

    def test_get__engagement_does_not_exist(self):
        """Trying to use GET with an engagement id that doesn't exist"""
        fake_uuid = "027c315e-3788-4c30-8c58-46723077e2f0"
        request = self.factory.get(self.view_url.format(fake_uuid))
        request.user = self.user_without_engagement
        response = self.view(request, fake_uuid)

        self.assertEqual(response.status_code, 404)

    def test_get__user_does_not_own_engagement(self):
        """Return 404 if user requests engagement they do not own."""
        request = self.factory.get(self.view_url.format(self.workflow_engagement.id))
        request.user = self.user_without_engagement
        response = self.view(request, self.workflow_engagement.id)

        self.assertEqual(response.status_code, 404)

    def test_get__authenticated_engagement(self):
        """Returned specified engagement for requesting user."""
        request = self.factory.get(self.view_url.format(self.workflow_engagement.id))
        request.user = self.user_with_engagement
        response = self.view(request, self.workflow_engagement.id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data["workflow_collection"],
            f"http://testserver/api/workflow_system/collections/{self.workflow_engagement.workflow_collection.id}/",
        )
        self.assertEqual(
            dateutil.parser.parse(response.data["started"]),
            self.workflow_engagement.started,
        )

    def test_patch__unauthenticated_engagement(self):
        """Return 404 error if trying to patch unknown engagement."""
        fake_uuiid = "4f84f799-9cc5-43d3-0000-24840b7eb8ce"

        request = self.factory.patch(
            self.view_url.format(fake_uuiid), data={}, format="json"
        )
        request.user = self.user_with_engagement
        response = self.view(request, fake_uuiid)

        self.assertEqual(response.status_code, 404)
        self.assertDictEqual(
            response.data,
            {"detail": ErrorDetail(string="Not found.", code="not_found")},
        )

        time_stamp = timezone.now()
        request = self.factory.patch(
            self.view_url.format(self.workflow_engagement.id),
            data={"finished": time_stamp},
            format="json",
        )
        request.user = self.user_with_engagement
        response = self.view(request, self.workflow_engagement.id)

        self.assertEqual(response.status_code, 200)

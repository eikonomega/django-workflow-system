from dateutil.relativedelta import relativedelta
from django.test import TestCase

from rest_framework.test import APIRequestFactory

from django_workflow_system.api.tests.factories import (
    UserFactory,
    WorkflowFactory,
    WorkflowCollectionFactory,
    WorkflowCollectionEngagementFactory,
    WorkflowStepFactory,
)
from django_workflow_system.api.views.user.workflows import (
    WorkflowCollectionEngagementsView,
)


class TestWorkflowCollectionEngagementsView(TestCase):
    """Test WorkflowEngagementsView."""

    def setUp(self):
        self.view = WorkflowCollectionEngagementsView.as_view()
        self.view_url = "/users/self/workflows/engagements/"
        self.factory = APIRequestFactory()

        self.maxDiff = 1000

        ## USER WITH ENGAGEMENT ##
        self.user_with_engagement = UserFactory()
        self.workflow = WorkflowFactory()
        self.workflow_collection = WorkflowCollectionFactory(
            workflow_set=[self.workflow]
        )
        self.workflow_user_engagement = WorkflowCollectionEngagementFactory(
            user=self.user_with_engagement,
            workflow_collection=self.workflow_collection,
        )
        self.workflow_step = WorkflowStepFactory(workflow=self.workflow)
        self.workflow_step_2 = WorkflowStepFactory(workflow=self.workflow)

        ## USER WITHOUT ENGAGEMENT ##
        self.user_without_engagement = UserFactory(username="Engagementless")

    def test_get__user_has_no_engagements(self):
        """Return a 200 if requesting user has no engagements."""
        request = self.factory.get(self.view_url)
        request.user = UserFactory()
        response = self.view(request)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.data)

    def test_get__user_has_engagements(self):
        """Return engagements for requesting user."""
        request = self.factory.get(self.view_url)
        request.user = self.user_with_engagement
        response = self.view(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        for engagement in response.data:
            self.assertListEqual(
                list(engagement.keys()),
                [
                    "detail",
                    "workflow_collection",
                    "started",
                    "finished",
                ],
            )

    def test_post__incomplete_payload(self):
        """Incomplete JSON payload returns a 400 error."""
        request = self.factory.post(self.view_url, data={}, format="json")
        request.user = self.user_without_engagement
        response = self.view(request)

        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(
            response.data, {"workflow_collection": ["This field is required."]}
        )

    def test_post__valid_payload(self):
        """Valid JSON payloads return 201."""
        request = self.factory.post(
            self.view_url,
            data={
                "workflow_collection": f"http://testserver/api/workflow_system/collections/"
                f"{self.workflow_user_engagement.workflow_collection.id}/"
            },
            format="json",
        )

        request.user = self.user_without_engagement
        response = self.view(request)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(response.data), 6)
        self.assertEqual(
            response.data["workflow_collection"],
            f"http://testserver/api/workflow_system/collections/"
            f"{self.workflow_user_engagement.workflow_collection.id}/",
        )
        self.assertEqual(
            response.data["state"],
            {
                "next_step_id": self.workflow_step.id,
                "next_workflow": f"http://testserver/api/workflow_system/workflows/{self.workflow_step.workflow.id}/",
                "prev_workflow": None,
                "prev_step_id": None,
                "previously_completed_workflows": [],
                "steps_completed_in_collection": 0,
                "steps_completed_in_workflow": 0,
                "steps_in_collection": 2,
                "steps_in_workflow": 2,
            },
        )

    def test_post__existing_incomplete_engagement(self):
        """Attempting to recreate an existing engagement results in a 409."""
        request = self.factory.post(
            self.view_url,
            data={
                "workflow_collection": f"http://testserver/api/workflow_system/collections/"
                f"{self.workflow_user_engagement.workflow_collection.id}/"
            },
            format="json",
        )
        request.user = self.user_with_engagement
        response = self.view(request)

        self.assertEqual(response.status_code, 409)

    def test_post__finish_before_start(self):
        """
        Attempting to POST a finish date prior to
        a start date results in a 400.
        """
        request = self.factory.post(
            self.view_url,
            data={
                "workflow_collection": "http://testserver/api/workflow_system/collections/{}/".format(
                    self.workflow_user_engagement.workflow_collection.id
                ),
                "finished": (
                    self.workflow_user_engagement.started - relativedelta(days=1)
                ),
            },
            format="json",
        )
        request.user = self.user_with_engagement
        response = self.view(request)

        self.assertEqual(response.status_code, 400)
